import csv
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete, select, text

from factory import db
from main import app
from models import InventoryItem, MenuItem, MenuItemRecipe, Order, Restaurant, RevenueDaily
from services.revenue_daily_service import rebuild_revenue_daily_for_restaurant


DEFAULT_RESTAURANT_EMAIL = "admin@empresa-demo.com"


@dataclass(frozen=True)
class RecipeIngredient:
    name: str
    quantity_required: float
    unit: str = "un"


RECIPE_TEMPLATES: dict[str, list[RecipeIngredient]] = {
    "poke bowl": [
        RecipeIngredient("Arroz para sushi", 1, "porcao"),
        RecipeIngredient("Peixe fresco", 1, "porcao"),
        RecipeIngredient("Molho poke", 1, "dose"),
        RecipeIngredient("Legumes frescos", 1, "porcao"),
    ],
    "ramen": [
        RecipeIngredient("Massa para ramen", 1, "porcao"),
        RecipeIngredient("Caldo oriental", 1, "tigela"),
        RecipeIngredient("Proteina do ramen", 1, "porcao"),
        RecipeIngredient("Cebolinha", 1, "porcao"),
    ],
    "feijoada": [
        RecipeIngredient("Feijao preto", 1, "porcao"),
        RecipeIngredient("Mix de carnes", 1, "porcao"),
        RecipeIngredient("Arroz branco", 1, "porcao"),
        RecipeIngredient("Farofa", 1, "porcao"),
    ],
    "classic burger": [
        RecipeIngredient("Pao de burger", 1, "un"),
        RecipeIngredient("Hamburguer bovino", 1, "un"),
        RecipeIngredient("Queijo", 1, "fatia"),
        RecipeIngredient("Molho da casa", 1, "dose"),
    ],
    "smash burger": [
        RecipeIngredient("Pao de burger", 1, "un"),
        RecipeIngredient("Blend smash", 1, "un"),
        RecipeIngredient("Queijo", 2, "fatias"),
        RecipeIngredient("Picles", 1, "porcao"),
    ],
    "margherita pizza": [
        RecipeIngredient("Massa de pizza", 1, "un"),
        RecipeIngredient("Molho de tomate", 1, "porcao"),
        RecipeIngredient("Muçarela", 1, "porcao"),
        RecipeIngredient("Manjericao", 1, "porcao"),
    ],
    "pepperoni pizza": [
        RecipeIngredient("Massa de pizza", 1, "un"),
        RecipeIngredient("Molho de tomate", 1, "porcao"),
        RecipeIngredient("Muçarela", 1, "porcao"),
        RecipeIngredient("Pepperoni", 1, "porcao"),
    ],
    "veggie pizza": [
        RecipeIngredient("Massa de pizza", 1, "un"),
        RecipeIngredient("Molho de tomate", 1, "porcao"),
        RecipeIngredient("Muçarela", 1, "porcao"),
        RecipeIngredient("Legumes grelhados", 1, "porcao"),
    ],
    "caesar salad": [
        RecipeIngredient("Alface romana", 1, "porcao"),
        RecipeIngredient("Croutons", 1, "porcao"),
        RecipeIngredient("Molho caesar", 1, "dose"),
        RecipeIngredient("Parmesao", 1, "porcao"),
    ],
    "greek salad": [
        RecipeIngredient("Mix de folhas", 1, "porcao"),
        RecipeIngredient("Tomate", 1, "porcao"),
        RecipeIngredient("Pepino", 1, "porcao"),
        RecipeIngredient("Queijo feta", 1, "porcao"),
    ],
    "grilled salmon": [
        RecipeIngredient("Salmao", 1, "posta"),
        RecipeIngredient("Legumes grelhados", 1, "porcao"),
        RecipeIngredient("Molho de ervas", 1, "dose"),
    ],
    "bbq ribs": [
        RecipeIngredient("Costela suina", 1, "porcao"),
        RecipeIngredient("Molho barbecue", 1, "dose"),
        RecipeIngredient("Batata rustica", 1, "porcao"),
    ],
    "pad thai": [
        RecipeIngredient("Macarrao de arroz", 1, "porcao"),
        RecipeIngredient("Molho pad thai", 1, "dose"),
        RecipeIngredient("Proteina do pad thai", 1, "porcao"),
        RecipeIngredient("Amendoim", 1, "porcao"),
    ],
    "chicken curry": [
        RecipeIngredient("Frango em cubos", 1, "porcao"),
        RecipeIngredient("Molho curry", 1, "porcao"),
        RecipeIngredient("Arroz jasmine", 1, "porcao"),
    ],
    "tacos": [
        RecipeIngredient("Tortilla", 2, "un"),
        RecipeIngredient("Recheio de taco", 1, "porcao"),
        RecipeIngredient("Guacamole", 1, "dose"),
        RecipeIngredient("Pico de gallo", 1, "dose"),
    ],
    "burrito": [
        RecipeIngredient("Tortilla grande", 1, "un"),
        RecipeIngredient("Arroz temperado", 1, "porcao"),
        RecipeIngredient("Feijao temperado", 1, "porcao"),
        RecipeIngredient("Recheio de burrito", 1, "porcao"),
    ],
    "sushi combo": [
        RecipeIngredient("Arroz para sushi", 1, "porcao"),
        RecipeIngredient("Peixe fresco", 1, "porcao"),
        RecipeIngredient("Nori", 1, "folha"),
        RecipeIngredient("Cream cheese", 1, "porcao"),
    ],
}


DEFAULT_RECIPE = [
    RecipeIngredient("Base do prato", 1, "porcao"),
    RecipeIngredient("Proteina principal", 1, "porcao"),
    RecipeIngredient("Acompanhamento", 1, "porcao"),
]


def get_dataset_path() -> Path:
    backend_dataset_path = Path(__file__).resolve().parent / "datasets" / "deliveries_train.csv"

    if backend_dataset_path.exists():
        return backend_dataset_path

    return Path(__file__).resolve().parents[1] / "ia" / "datasets" / "deliveries_train.csv"


def format_dish_name(value: str) -> str:
    return value.replace("_", " ").title()


def build_order_notes(row: dict[str, str]) -> str:
    return (
        f"Bairro: {row['delivery_neighborhood']} | "
        f"Clima: {row['weather']} | "
        f"Transito: {row['traffic_level']} | "
        f"Tempo entrega: {row['delivery_time_minutes']} min"
    )


def get_recipe_for_dish(dish_name: str) -> list[RecipeIngredient]:
    normalized_name = dish_name.strip().lower()
    return RECIPE_TEMPLATES.get(normalized_name, DEFAULT_RECIPE)


def load_dataset_rows(dataset_path: Path) -> list[dict[str, str]]:
    with dataset_path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def seed_admin_revenue_and_menu():
    restaurant_email = os.getenv("RESTAURANT_ADMIN_EMAIL", DEFAULT_RESTAURANT_EMAIL)
    dataset_path = get_dataset_path()

    restaurant = db.session.scalars(
        select(Restaurant).filter_by(email=restaurant_email)
    ).first()

    if restaurant is None:
        raise RuntimeError(
            f"Restaurant {restaurant_email} not found. Run populate_database.py first."
        )

    rows = load_dataset_rows(dataset_path)

    if not rows:
        raise RuntimeError(f"Dataset {dataset_path} is empty.")

    menu_item_ids = db.session.scalars(
        select(MenuItem.id).filter_by(restaurant_id=restaurant.id)
    ).all()

    # Apaga primeiro os pedidos antigos da tabela restaurant_order
    db.session.execute(
        text("DELETE FROM restaurant_order WHERE restaurant_id = :restaurant_id"),
        {"restaurant_id": restaurant.id},
    )
    db.session.execute(delete(RevenueDaily).where(RevenueDaily.restaurant_id == restaurant.id))

    if menu_item_ids:
        db.session.execute(
            delete(MenuItemRecipe).where(MenuItemRecipe.menu_item_id.in_(menu_item_ids))
        )

    db.session.execute(delete(MenuItem).where(MenuItem.restaurant_id == restaurant.id))
    db.session.execute(delete(InventoryItem).where(InventoryItem.restaurant_id == restaurant.id))
    db.session.flush()

    dish_prices: dict[str, list[float]] = defaultdict(list)
    dish_order_counts: Counter[str] = Counter()

    for row in rows:
        dish_name = format_dish_name(row["main_dish"].strip())
        dish_prices[dish_name].append(float(row["order_price"]))
        dish_order_counts[dish_name] += 1

    inventory_usage_totals: Counter[str] = Counter()
    inventory_units: dict[str, str] = {}
    menu_items_by_name: dict[str, MenuItem] = {}

    for dish_name, prices in dish_prices.items():
        recipe = get_recipe_for_dish(dish_name)

        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name=dish_name,
            price_cents=int(round((sum(prices) / len(prices)) * 100)),
            ingredients=[ingredient.name for ingredient in recipe],
        )

        db.session.add(menu_item)
        menu_items_by_name[dish_name] = menu_item

        for ingredient in recipe:
            inventory_usage_totals[ingredient.name] += (
                ingredient.quantity_required * dish_order_counts[dish_name]
            )
            inventory_units[ingredient.name] = ingredient.unit

    db.session.flush()

    inventory_items_by_name: dict[str, InventoryItem] = {}

    for ingredient_name, total_usage in inventory_usage_totals.items():
        buffer_quantity = max(20.0, total_usage * 0.35)

        inventory_item = InventoryItem(
            restaurant_id=restaurant.id,
            name=ingredient_name,
            unit=inventory_units.get(ingredient_name, "un"),
            quantity_available=round(total_usage + buffer_quantity, 2),
            minimum_quantity=round(max(5.0, total_usage * 0.1), 2),
        )

        db.session.add(inventory_item)
        inventory_items_by_name[ingredient_name] = inventory_item

    db.session.flush()

    for dish_name, menu_item in menu_items_by_name.items():
        for ingredient in get_recipe_for_dish(dish_name):
            db.session.add(
                MenuItemRecipe(
                    menu_item_id=menu_item.id,
                    inventory_item_id=inventory_items_by_name[ingredient.name].id,
                    quantity_required=ingredient.quantity_required,
                )
            )

    imported_orders = 0

    for row in rows:
        order_time = datetime.fromisoformat(row["order_time"])
        dish_name = format_dish_name(row["main_dish"].strip())

        order = Order(
            restaurant_id=restaurant.id,
            customer_name=row["customer_first_name"].strip(),
            menu_item_id=menu_items_by_name[dish_name].id,
            main_dish=dish_name,
            order_price_cents=int(round(float(row["order_price"]) * 100)),
            status="delivered",
            stock_deducted=False,
            notes=build_order_notes(row),
            created_at=order_time,
            updated_at=order_time,
        )

        db.session.add(order)
        imported_orders += 1

    db.session.commit()
    rebuild_revenue_daily_for_restaurant(restaurant.id)

    print(
        f"Seeded {len(menu_items_by_name)} menu items, "
        f"{len(inventory_items_by_name)} inventory items and "
        f"{imported_orders} revenue orders into restaurant {restaurant.email} "
        f"from {dataset_path.name}"
    )


if __name__ == "__main__":
    with app.app_context():
        seed_admin_revenue_and_menu()
