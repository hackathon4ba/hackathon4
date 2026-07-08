import os

from factory import db
from main import app
from models import Restaurant, User
from sqlalchemy import select


DEFAULT_ADMIN_EMAIL = "admin@hackathon.local"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_RESTAURANT_EMAIL = "admin@empresa-demo.com"
DEFAULT_RESTAURANT_PASSWORD = "admin123"
DEFAULT_RESTAURANT_NAME = "Empresa Admin Demo"


def populate_admin_user():
    admin_email = os.getenv("ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
    admin_password = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)

    existing_user = db.session.scalars(
        select(User).filter_by(email=admin_email)
    ).first()

    if existing_user is None:
        existing_user = User(email=admin_email)
        db.session.add(existing_user)

    existing_user.password = admin_password
    db.session.commit()

    print(f"Admin user ready: {admin_email}")


def populate_admin_restaurant():
    restaurant_email = os.getenv("RESTAURANT_ADMIN_EMAIL", DEFAULT_RESTAURANT_EMAIL)
    restaurant_password = os.getenv(
        "RESTAURANT_ADMIN_PASSWORD", DEFAULT_RESTAURANT_PASSWORD
    )
    restaurant_name = os.getenv("RESTAURANT_ADMIN_NAME", DEFAULT_RESTAURANT_NAME)

    restaurant = db.session.scalars(
        select(Restaurant).filter_by(email=restaurant_email)
    ).first()

    if restaurant is None:
        restaurant = Restaurant(
            name=restaurant_name,
            email=restaurant_email,
            phone="+5511999999999",
            address="Rua Demo, 123",
            cuisine_type="Operacao seed do dashboard",
            is_active=True,
        )
        db.session.add(restaurant)

    restaurant.name = restaurant_name
    restaurant.phone = "+5511999999999"
    restaurant.address = "Rua Demo, 123"
    restaurant.cuisine_type = "Operacao seed do dashboard"
    restaurant.is_active = True
    restaurant.password = restaurant_password

    db.session.commit()

    print(f"Admin restaurant ready: {restaurant_email}")


if __name__ == "__main__":
    with app.app_context():
        populate_admin_user()
        populate_admin_restaurant()
