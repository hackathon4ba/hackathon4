from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from spectree import Response
from sqlalchemy import select

from factory import api, db
from models import MenuItem, Restaurant
from models.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from utils.response_schema import GenericResponse

menu_controller = Blueprint("menu_controller", __name__, url_prefix="/restaurants/menu")


class MenuItemsResponse(GenericResponse):
    data: list[MenuItemResponse]


def get_authenticated_restaurant():
    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return None

    return current_user


def normalize_ingredients(ingredients: list[str]) -> list[str]:
    return [ingredient.strip() for ingredient in ingredients if ingredient.strip()]


@menu_controller.get("/items")
@api.validate(
    resp=Response(
        HTTP_200=MenuItemsResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def list_menu_items():
    """
    List menu items for the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    items = db.session.scalars(
        select(MenuItem)
        .filter_by(restaurant_id=restaurant.id)
        .order_by(MenuItem.name.asc())
    ).all()

    data = [MenuItemResponse.model_validate(item).to_response_dict() for item in items]

    return {"msg": "Menu items fetched successfully.", "data": data}, 200


@menu_controller.post("/items")
@api.validate(
    json=MenuItemCreate,
    resp=Response(
        HTTP_201=MenuItemResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def create_menu_item():
    """
    Create a menu item for the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    data = request.json
    name = data["name"].strip()
    ingredients = normalize_ingredients(data["ingredients"])

    if not name:
        return {"msg": "Menu item name is required."}, 400

    if not ingredients:
        return {"msg": "At least one ingredient is required."}, 400

    item = MenuItem(
        restaurant_id=restaurant.id,
        name=name,
        price_cents=round(data["price"] * 100),
        ingredients=ingredients,
    )
    db.session.add(item)
    db.session.commit()

    return MenuItemResponse.model_validate(item).to_response_dict(), 201


@menu_controller.patch("/items/<int:item_id>")
@api.validate(
    json=MenuItemUpdate,
    resp=Response(
        HTTP_200=MenuItemResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def update_menu_item(item_id: int):
    """
    Update a menu item from the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.get(MenuItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        return {"msg": "Menu item not found."}, 404

    data = request.json

    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        if not name:
            return {"msg": "Menu item name cannot be empty."}, 400
        item.name = name

    if "price" in data and data["price"] is not None:
        item.price_cents = round(data["price"] * 100)

    if "ingredients" in data and data["ingredients"] is not None:
        ingredients = normalize_ingredients(data["ingredients"])
        if not ingredients:
            return {"msg": "At least one ingredient is required."}, 400
        item.ingredients = ingredients

    db.session.commit()

    return MenuItemResponse.model_validate(item).to_response_dict(), 200


@menu_controller.delete("/items/<int:item_id>")
@api.validate(
    resp=Response(
        HTTP_200=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def delete_menu_item(item_id: int):
    """
    Delete a menu item from the logged restaurant.
    """

    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.get(MenuItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        return {"msg": "Menu item not found."}, 404

    db.session.delete(item)
    db.session.commit()

    return {"msg": "Menu item deleted successfully."}, 200
