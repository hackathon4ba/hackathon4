from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from pydantic import BaseModel
from spectree import Response
from sqlalchemy import select

from factory import api, db
from models import InventoryItem, Restaurant
from models.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from utils.response_schema import GenericResponse

inventory_controller = Blueprint(
    "inventory_controller", __name__, url_prefix="/restaurants/inventory"
)


class InventoryItemsResponse(BaseModel):
    data: list[InventoryItemResponse]
    msg: str


def get_authenticated_restaurant():
    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return None

    return current_user


def serialize_inventory_item(item: InventoryItem) -> dict:
    payload = InventoryItemResponse.model_validate(item).to_response_dict()
    payload["is_low_stock"] = item.quantity_available <= item.minimum_quantity
    return payload


@inventory_controller.get("/items")
@api.validate(
    resp=Response(
        HTTP_200=InventoryItemsResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["inventory"],
)
@jwt_required()
def list_inventory_items():
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    items = db.session.scalars(
        select(InventoryItem)
        .filter_by(restaurant_id=restaurant.id)
        .order_by(InventoryItem.name.asc())
    ).all()

    return {
        "msg": "Inventory items fetched successfully.",
        "data": [serialize_inventory_item(item) for item in items],
    }, 200


@inventory_controller.post("/items")
@api.validate(
    json=InventoryItemCreate,
    resp=Response(
        HTTP_201=InventoryItemResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["inventory"],
)
@jwt_required()
def create_inventory_item():
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    data = request.json
    name = data["name"].strip()
    unit = data.get("unit", "un").strip()

    if not name:
        return {"msg": "Inventory item name is required."}, 400

    if not unit:
        return {"msg": "Inventory item unit is required."}, 400

    existing_item = db.session.scalars(
        select(InventoryItem).filter_by(restaurant_id=restaurant.id, name=name)
    ).first()
    if existing_item is not None:
        return {"msg": "Inventory item already exists for this restaurant."}, 400

    item = InventoryItem(
        restaurant_id=restaurant.id,
        name=name,
        unit=unit,
        quantity_available=data["quantity_available"],
        minimum_quantity=data.get("minimum_quantity", 0),
    )
    db.session.add(item)
    db.session.commit()

    return serialize_inventory_item(item), 201


@inventory_controller.patch("/items/<int:item_id>")
@api.validate(
    json=InventoryItemUpdate,
    resp=Response(
        HTTP_200=InventoryItemResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["inventory"],
)
@jwt_required()
def update_inventory_item(item_id: int):
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.get(InventoryItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        return {"msg": "Inventory item not found."}, 404

    data = request.json

    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        if not name:
            return {"msg": "Inventory item name cannot be empty."}, 400

        duplicate_item = db.session.scalars(
            select(InventoryItem).filter(
                InventoryItem.restaurant_id == restaurant.id,
                InventoryItem.name == name,
                InventoryItem.id != item.id,
            )
        ).first()
        if duplicate_item is not None:
            return {"msg": "Inventory item already exists for this restaurant."}, 400

        item.name = name

    if "unit" in data and data["unit"] is not None:
        unit = data["unit"].strip()
        if not unit:
            return {"msg": "Inventory item unit cannot be empty."}, 400
        item.unit = unit

    if "quantity_available" in data and data["quantity_available"] is not None:
        item.quantity_available = data["quantity_available"]

    if "minimum_quantity" in data and data["minimum_quantity"] is not None:
        item.minimum_quantity = data["minimum_quantity"]

    db.session.commit()

    return serialize_inventory_item(item), 200


@inventory_controller.delete("/items/<int:item_id>")
@api.validate(
    resp=Response(
        HTTP_200=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["inventory"],
)
@jwt_required()
def delete_inventory_item(item_id: int):
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.get(InventoryItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        return {"msg": "Inventory item not found."}, 404

    db.session.delete(item)
    db.session.commit()

    return {"msg": "Inventory item deleted successfully."}, 200

