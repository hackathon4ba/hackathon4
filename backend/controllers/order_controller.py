from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from pydantic import BaseModel
from spectree import Response
from sqlalchemy import select

from factory import api, db
from models import Order, Restaurant
from models.order import ORDER_STATUSES, OrderCreate, OrderResponse, OrderUpdate
from services.inventory_service import (
    InventoryError,
    consume_menu_item_stock,
    get_menu_item_for_restaurant,
    restore_menu_item_stock,
    status_requires_stock,
)
from services.revenue_daily_service import sync_revenue_daily_for_dates
from utils.response_schema import GenericResponse

order_controller = Blueprint("order_controller", __name__, url_prefix="/restaurants/orders")


class OrdersResponse(BaseModel):
    data: list[OrderResponse]
    msg: str
    meta: dict[str, int]


def get_authenticated_restaurant():
    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return None

    return current_user


def normalize_status(status: str) -> str:
    return status.strip().lower()


def validate_status(status: str):
    normalized_status = normalize_status(status)
    if normalized_status not in ORDER_STATUSES:
        return None

    return normalized_status


@order_controller.get("")
@api.validate(
    resp=Response(
        HTTP_200=OrdersResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["orders"],
)
@jwt_required()
def list_orders():
    """
    List orders for the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    query = select(Order).filter_by(restaurant_id=restaurant.id)

    status = request.args.get("status")
    if status:
        normalized_status = validate_status(status)
        if normalized_status is None:
            return {"msg": "Invalid order status."}, 400
        query = query.filter_by(status=normalized_status)

    search = request.args.get("q", "").strip()
    page = request.args.get("page", default=1, type=int) or 1
    page_size = request.args.get("pageSize", default=10, type=int) or 10

    if page < 1 or page_size < 1:
        return {"msg": "Invalid pagination parameters."}, 400

    page_size = min(page_size, 100)
    orders = db.session.scalars(query.order_by(Order.created_at.desc())).all()

    if search:
        lowered_search = search.lower()
        orders = [
            order
            for order in orders
            if lowered_search in order.customer_name.lower()
            or lowered_search in order.main_dish.lower()
            or lowered_search in str(order.id)
        ]

    total = len(orders)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_orders = orders[start:end]

    data = [
        OrderResponse.model_validate(order).to_response_dict()
        for order in paginated_orders
    ]
    return {
        "msg": "Orders fetched successfully.",
        "data": data,
        "meta": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": total_pages,
        },
    }, 200


@order_controller.post("")
@api.validate(
    json=OrderCreate,
    resp=Response(
        HTTP_201=OrderResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["orders"],
)
@jwt_required()
def create_order():
    """
    Create an order for the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    data = request.json
    customer_name = data["customer_name"].strip()
    main_dish = data["main_dish"].strip()
    status = validate_status(data.get("status", "pending"))

    if not customer_name or not main_dish:
        return {"msg": "Customer name and main dish are required."}, 400

    if status is None:
        return {"msg": "Invalid order status."}, 400

    menu_item = get_menu_item_for_restaurant(restaurant.id, main_dish)
    if menu_item is None:
        return {"msg": "Menu item not found for this restaurant."}, 400

    order = Order(
        restaurant_id=restaurant.id,
        menu_item_id=menu_item.id,
        customer_name=customer_name,
        main_dish=menu_item.name,
        order_price_cents=round(data["price"] * 100),
        status=status,
        stock_deducted=False,
        notes=data.get("notes"),
    )

    try:
        if status_requires_stock(status):
            consume_menu_item_stock(menu_item)
            order.stock_deducted = True

        db.session.add(order)
        db.session.commit()
        sync_revenue_daily_for_dates(
            restaurant.id,
            [order.created_at.date()],
        )
    except InventoryError as error:
        db.session.rollback()
        return {"msg": str(error)}, 400

    return OrderResponse.model_validate(order).to_response_dict(), 201


@order_controller.get("/<int:order_id>")
@api.validate(
    resp=Response(
        HTTP_200=OrderResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["orders"],
)
@jwt_required()
def get_order(order_id: int):
    """
    Get an order from the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    order = db.session.get(Order, order_id)
    if order is None or order.restaurant_id != restaurant.id:
        return {"msg": "Order not found."}, 404

    return OrderResponse.model_validate(order).to_response_dict(), 200


@order_controller.patch("/<int:order_id>")
@api.validate(
    json=OrderUpdate,
    resp=Response(
        HTTP_200=OrderResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["orders"],
)
@jwt_required()
def update_order(order_id: int):
    """
    Update an order from the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    order = db.session.get(Order, order_id)
    if order is None or order.restaurant_id != restaurant.id:
        return {"msg": "Order not found."}, 404

    data = request.json
    affected_revenue_dates = {order.created_at.date()}

    if "customer_name" in data and data["customer_name"] is not None:
        customer_name = data["customer_name"].strip()
        if not customer_name:
            return {"msg": "Customer name cannot be empty."}, 400
        order.customer_name = customer_name

    requested_main_dish = None
    if "main_dish" in data and data["main_dish"] is not None:
        main_dish = data["main_dish"].strip()
        if not main_dish:
            return {"msg": "Main dish cannot be empty."}, 400
        requested_main_dish = main_dish
    else:
        main_dish = order.main_dish

    if "price" in data and data["price"] is not None:
        order.order_price_cents = round(data["price"] * 100)

    if "status" in data and data["status"] is not None:
        status = validate_status(data["status"])
        if status is None:
            return {"msg": "Invalid order status."}, 400
    else:
        status = order.status

    if "notes" in data:
        order.notes = data["notes"]

    next_menu_item = None
    if requested_main_dish is not None or order.menu_item_id is not None or (
        not order.stock_deducted and status_requires_stock(status)
    ):
        next_menu_item = get_menu_item_for_restaurant(order.restaurant_id, main_dish)
        if next_menu_item is None:
            return {"msg": "Menu item not found for this restaurant."}, 400

    try:
        if order.stock_deducted:
            if next_menu_item is None and status_requires_stock(status):
                return {"msg": "Menu item not found for stock adjustment."}, 400

            if (
                next_menu_item is not None
                and order.menu_item_id != next_menu_item.id
            ) or not status_requires_stock(status):
                if order.menu_item is None:
                    return {"msg": "Original menu item not found for stock adjustment."}, 400
                restore_menu_item_stock(order.menu_item)
                order.stock_deducted = False

        if status_requires_stock(status) and not order.stock_deducted:
            if next_menu_item is None:
                return {"msg": "Menu item not found for stock adjustment."}, 400
            consume_menu_item_stock(next_menu_item)
            order.stock_deducted = True

        if next_menu_item is not None:
            order.menu_item_id = next_menu_item.id
            order.main_dish = next_menu_item.name
        elif requested_main_dish is not None:
            order.main_dish = requested_main_dish
        order.status = status

        db.session.commit()
        sync_revenue_daily_for_dates(
            restaurant.id,
            affected_revenue_dates,
        )
    except InventoryError as error:
        db.session.rollback()
        return {"msg": str(error)}, 400

    return OrderResponse.model_validate(order).to_response_dict(), 200


@order_controller.delete("/<int:order_id>")
@api.validate(
    resp=Response(
        HTTP_200=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["orders"],
)
@jwt_required()
def delete_order(order_id: int):
    """
    Delete an order from the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    order = db.session.get(Order, order_id)
    if order is None or order.restaurant_id != restaurant.id:
        return {"msg": "Order not found."}, 404

    affected_revenue_dates = {order.created_at.date()}
    db.session.delete(order)
    db.session.commit()
    sync_revenue_daily_for_dates(
        restaurant.id,
        affected_revenue_dates,
    )

    return {"msg": "Order deleted successfully."}, 200
