from datetime import datetime, timezone

from pydantic import BaseModel, Field

from factory import db
from utils.response_schema import OrmBase


class MenuItem(db.Model):
    __tablename__ = "menu_item"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False, index=True
    )
    name = db.Column(db.String(128), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    restaurant = db.relationship("Restaurant", back_populates="menu_items")
    recipe_entries = db.relationship(
        "MenuItemRecipe", back_populates="menu_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MenuItem {self.name}>"


class MenuItemCreate(BaseModel):
    name: str
    price: float = Field(gt=0)
    ingredients: list[str] = Field(min_length=1)


class MenuItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)
    ingredients: list[str] | None = None


class MenuItemResponse(OrmBase):
    restaurant_id: int
    name: str
    price_cents: int
    ingredients: list[str]
    created_at: datetime
    updated_at: datetime
