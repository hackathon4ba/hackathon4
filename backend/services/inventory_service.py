from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from factory import db
from models import InventoryItem, MenuItem, MenuItemRecipe


class InventoryError(Exception):
    pass


def status_requires_stock(status: str) -> bool:
    return status != "cancelled"


def get_menu_item_for_restaurant(restaurant_id: int, main_dish: str) -> MenuItem | None:
    normalized_name = main_dish.strip().lower()
    if not normalized_name:
        return None

    return db.session.scalars(
        select(MenuItem)
        .options(
            joinedload(MenuItem.recipe_entries).joinedload(MenuItemRecipe.inventory_item)
        )
        .filter(
            MenuItem.restaurant_id == restaurant_id,
            func.lower(MenuItem.name) == normalized_name,
        )
    ).first()


def get_inventory_item_for_restaurant(
    restaurant_id: int, inventory_item_id: int
) -> InventoryItem | None:
    return db.session.scalars(
        select(InventoryItem).filter_by(
            id=inventory_item_id, restaurant_id=restaurant_id
        )
    ).first()


def consume_menu_item_stock(menu_item: MenuItem):
    recipe_entries = list(menu_item.recipe_entries)
    if not recipe_entries:
        raise InventoryError(
            f"The menu item '{menu_item.name}' does not have a stock recipe configured."
        )

    for entry in recipe_entries:
        inventory_item = entry.inventory_item
        if inventory_item is None:
            raise InventoryError("Recipe contains an invalid inventory item.")

        if inventory_item.quantity_available < entry.quantity_required:
            raise InventoryError(
                f"Insufficient stock for '{inventory_item.name}'. "
                f"Available: {inventory_item.quantity_available:g} {inventory_item.unit}. "
                f"Required: {entry.quantity_required:g} {inventory_item.unit}."
            )

    for entry in recipe_entries:
        entry.inventory_item.quantity_available -= entry.quantity_required


def restore_menu_item_stock(menu_item: MenuItem):
    for entry in menu_item.recipe_entries:
        if entry.inventory_item is not None:
            entry.inventory_item.quantity_available += entry.quantity_required
