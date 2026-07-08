import csv
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete, select

from factory import db
from main import app
from models import Order, Restaurant


DEFAULT_RESTAURANT_EMAIL = "admin@empresa-demo.com"


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


def seed_admin_orders():
    restaurant_email = os.getenv("RESTAURANT_ADMIN_EMAIL", DEFAULT_RESTAURANT_EMAIL)
    dataset_path = get_dataset_path()

    restaurant = db.session.scalars(
        select(Restaurant).filter_by(email=restaurant_email)
    ).first()
    if restaurant is None:
        raise RuntimeError(
            f"Restaurant {restaurant_email} not found. Run populate_database.py first."
        )

    db.session.execute(delete(Order).where(Order.restaurant_id == restaurant.id))

    imported_orders = 0
    with dataset_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            order_time = datetime.fromisoformat(row["order_time"])
            order = Order(
                restaurant_id=restaurant.id,
                customer_name=row["customer_first_name"].strip(),
                main_dish=format_dish_name(row["main_dish"].strip()),
                order_price_cents=int(round(float(row["order_price"]) * 100)),
                status="delivered",
                notes=build_order_notes(row),
                created_at=order_time,
                updated_at=order_time,
            )
            db.session.add(order)
            imported_orders += 1

    db.session.commit()
    print(
        f"Seeded {imported_orders} orders into restaurant {restaurant.email} "
        f"from {dataset_path.name}"
    )


if __name__ == "__main__":
    with app.app_context():
        seed_admin_orders()
