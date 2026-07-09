from datetime import datetime, timezone

from pydantic import BaseModel, Field

from factory import db
from utils.response_schema import OrmBase


ORDER_STATUSES = ("pending", "preparing", "out_for_delivery", "delivered", "cancelled")


class Order(db.Model):
    __tablename__ = "restaurant_order"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False, index=True
    )
    customer_name = db.Column(db.String(128), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=True)
    main_dish = db.Column(db.String(128), nullable=False)
    order_price_cents = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    stock_deducted = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    restaurant = db.relationship("Restaurant", back_populates="orders")
    menu_item = db.relationship("MenuItem")

    def __repr__(self) -> str:
        return f"<Order {self.id} {self.main_dish}>"


class OrderCreate(BaseModel):
    customer_name: str
    main_dish: str
    price: float = Field(gt=0)
    status: str = "pending"
    notes: str | None = None


class OrderUpdate(BaseModel):
    customer_name: str | None = None
    main_dish: str | None = None
    price: float | None = Field(default=None, gt=0)
    status: str | None = None
    notes: str | None = None


class OrderResponse(OrmBase):
    restaurant_id: int
    customer_name: str
    menu_item_id: int | None = None
    main_dish: str
    order_price_cents: int
    status: str
    stock_deducted: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
