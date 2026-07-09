from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from werkzeug.security import check_password_hash, generate_password_hash

from factory import db
from utils.response_schema import OrmBase


class Restaurant(db.Model):
    __tablename__ = "restaurant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(32), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    cuisine_type = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    menu_items = db.relationship(
        "MenuItem", back_populates="restaurant", cascade="all, delete-orphan"
    )
    inventory_items = db.relationship(
        "InventoryItem", back_populates="restaurant", cascade="all, delete-orphan"
    )
    daily_revenues = db.relationship(
        "RevenueDaily", back_populates="restaurant", cascade="all, delete-orphan"
    )
    orders = db.relationship(
        "Order", back_populates="restaurant", cascade="all, delete-orphan"
    )

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Restaurant {self.email}>"


class RestaurantCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[str] = None


class RestaurantLogin(BaseModel):
    email: str
    password: str


class RestaurantResponse(OrmBase):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[str] = None
    is_active: bool
    created_at: datetime


class RestaurantAuthResponse(BaseModel):
    access_token: str
    restaurant: RestaurantResponse
