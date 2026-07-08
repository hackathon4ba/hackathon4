from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from pydantic import BaseModel
from spectree import Response
from sqlalchemy import select

from factory import api, db
from models import Order, Restaurant
from models.order import ORDER_STATUSES, OrderCreate, OrderResponse, OrderUpdate
from utils.response_schema import GenericResponse

order_controller = Blueprint("order_controller", __name__, url_prefix="/restaurants/orders")


class OrdersResponse(BaseModel):
    data: list[OrderResponse]
    msg: str


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

    data = [OrderResponse.model_validate(order).to_response_dict() for order in orders]
    return {"msg": "Orders fetched successfully.", "data": data}, 200


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

    order = Order(
        restaurant_id=restaurant.id,
        customer_name=customer_name,
        main_dish=main_dish,
        order_price_cents=round(data["price"] * 100),
        status=status,
        notes=data.get("notes"),
    )
    db.session.add(order)
    db.session.commit()

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

    if "customer_name" in data and data["customer_name"] is not None:
        customer_name = data["customer_name"].strip()
        if not customer_name:
            return {"msg": "Customer name cannot be empty."}, 400
        order.customer_name = customer_name

    if "main_dish" in data and data["main_dish"] is not None:
        main_dish = data["main_dish"].strip()
        if not main_dish:
            return {"msg": "Main dish cannot be empty."}, 400
        order.main_dish = main_dish

    if "price" in data and data["price"] is not None:
        order.order_price_cents = round(data["price"] * 100)

    if "status" in data and data["status"] is not None:
        status = validate_status(data["status"])
        if status is None:
            return {"msg": "Invalid order status."}, 400
        order.status = status

    if "notes" in data:
        order.notes = data["notes"]

    db.session.commit()
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

    db.session.delete(order)
    db.session.commit()

    return {"msg": "Order deleted successfully."}, 200
