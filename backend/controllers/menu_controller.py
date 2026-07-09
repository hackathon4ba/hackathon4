from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from pydantic import BaseModel
from spectree import Response
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from factory import api, db
from models import InventoryItem, MenuItem, MenuItemRecipe, Restaurant
from models.inventory import MenuItemRecipeUpdate
from models.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from utils.response_schema import GenericResponse

menu_controller = Blueprint("menu_controller", __name__, url_prefix="/restaurants/menu")


class MenuItemsResponse(GenericResponse):
    data: list[dict]


class RecipeEntriesResponse(GenericResponse):
    data: list[dict]


class RecipeEntryResponse(BaseModel):
    id: int
    menu_item_id: int
    inventory_item_id: int
    inventory_item_name: str
    inventory_item_unit: str
    quantity_required: float


def get_authenticated_restaurant():
    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return None

    return current_user


def normalize_ingredients(ingredients: list[str]) -> list[str]:
    return [ingredient.strip() for ingredient in ingredients if ingredient.strip()]


def serialize_recipe_entry(entry: MenuItemRecipe) -> dict:
    return RecipeEntryResponse(
        id=entry.id,
        menu_item_id=entry.menu_item_id,
        inventory_item_id=entry.inventory_item_id,
        inventory_item_name=entry.inventory_item.name,
        inventory_item_unit=entry.inventory_item.unit,
        quantity_required=entry.quantity_required,
    ).model_dump(mode="json")


def serialize_menu_item(item: MenuItem) -> dict:
    payload = MenuItemResponse.model_validate(item).to_response_dict()
    payload["recipe"] = [
        serialize_recipe_entry(entry)
        for entry in sorted(item.recipe_entries, key=lambda recipe_entry: recipe_entry.id)
    ]
    return payload


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
        .options(joinedload(MenuItem.recipe_entries).joinedload(MenuItemRecipe.inventory_item))
        .filter_by(restaurant_id=restaurant.id)
        .order_by(MenuItem.name.asc())
    ).unique().all()

    data = [serialize_menu_item(item) for item in items]

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

    return serialize_menu_item(item), 201


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

    return serialize_menu_item(item), 200


@menu_controller.get("/items/<int:item_id>/recipe")
@api.validate(
    resp=Response(
        HTTP_200=RecipeEntriesResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def get_menu_item_recipe(item_id: int):
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.scalars(
        select(MenuItem)
        .options(joinedload(MenuItem.recipe_entries).joinedload(MenuItemRecipe.inventory_item))
        .filter_by(id=item_id, restaurant_id=restaurant.id)
    ).unique().first()
    if item is None:
        return {"msg": "Menu item not found."}, 404

    return {
        "msg": "Recipe fetched successfully.",
        "data": [serialize_recipe_entry(entry) for entry in item.recipe_entries],
    }, 200


@menu_controller.put("/items/<int:item_id>/recipe")
@api.validate(
    json=MenuItemRecipeUpdate,
    resp=Response(
        HTTP_200=RecipeEntriesResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["menu"],
)
@jwt_required()
def replace_menu_item_recipe(item_id: int):
    restaurant = get_authenticated_restaurant()
    if restaurant is None:
        return {"msg": "Restaurant token required."}, 403

    item = db.session.get(MenuItem, item_id)
    if item is None or item.restaurant_id != restaurant.id:
        return {"msg": "Menu item not found."}, 404

    entries = request.json["entries"]
    inventory_item_ids = [entry["inventory_item_id"] for entry in entries]
    if len(set(inventory_item_ids)) != len(inventory_item_ids):
        return {"msg": "Recipe contains duplicated inventory items."}, 400

    inventory_items = db.session.scalars(
        select(InventoryItem).filter(
            InventoryItem.restaurant_id == restaurant.id,
            InventoryItem.id.in_(inventory_item_ids),
        )
    ).all()
    inventory_by_id = {inventory_item.id: inventory_item for inventory_item in inventory_items}

    if len(inventory_by_id) != len(inventory_item_ids):
        return {"msg": "Recipe contains inventory items that do not belong to this restaurant."}, 400

    for recipe_entry in list(item.recipe_entries):
        db.session.delete(recipe_entry)
    db.session.flush()

    for entry in entries:
        db.session.add(
            MenuItemRecipe(
                menu_item_id=item.id,
                inventory_item_id=entry["inventory_item_id"],
                quantity_required=entry["quantity_required"],
            )
        )

    db.session.commit()

    refreshed_item = db.session.scalars(
        select(MenuItem)
        .options(joinedload(MenuItem.recipe_entries).joinedload(MenuItemRecipe.inventory_item))
        .filter_by(id=item.id)
    ).unique().first()

    return {
        "msg": "Recipe updated successfully.",
        "data": [
            serialize_recipe_entry(recipe_entry)
            for recipe_entry in refreshed_item.recipe_entries
        ],
    }, 200


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
