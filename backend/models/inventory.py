from datetime import datetime, timezone

from pydantic import BaseModel, Field

from factory import db
from utils.response_schema import OrmBase


class InventoryItem(db.Model):
    __tablename__ = "inventory_item"
    __table_args__ = (
        db.UniqueConstraint(
            "restaurant_id", "name", name="uq_inventory_item_restaurant_name"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False, index=True
    )
    name = db.Column(db.String(128), nullable=False)
    unit = db.Column(db.String(32), nullable=False, default="un")
    quantity_available = db.Column(db.Float, nullable=False, default=0)
    minimum_quantity = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    restaurant = db.relationship("Restaurant", back_populates="inventory_items")
    recipe_entries = db.relationship(
        "MenuItemRecipe", back_populates="inventory_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<InventoryItem {self.name}>"


class MenuItemRecipe(db.Model):
    __tablename__ = "menu_item_recipe"
    __table_args__ = (
        db.UniqueConstraint(
            "menu_item_id", "inventory_item_id", name="uq_menu_item_recipe_item"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(
        db.Integer, db.ForeignKey("menu_item.id"), nullable=False, index=True
    )
    inventory_item_id = db.Column(
        db.Integer, db.ForeignKey("inventory_item.id"), nullable=False, index=True
    )
    quantity_required = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    menu_item = db.relationship("MenuItem", back_populates="recipe_entries")
    inventory_item = db.relationship("InventoryItem", back_populates="recipe_entries")

    def __repr__(self) -> str:
        return f"<MenuItemRecipe menu_item={self.menu_item_id} inventory_item={self.inventory_item_id}>"


class InventoryItemCreate(BaseModel):
    name: str
    unit: str = Field(default="un", min_length=1, max_length=32)
    quantity_available: float = Field(ge=0)
    minimum_quantity: float = Field(default=0, ge=0)


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=32)
    quantity_available: float | None = Field(default=None, ge=0)
    minimum_quantity: float | None = Field(default=None, ge=0)


class RecipeEntryPayload(BaseModel):
    inventory_item_id: int
    quantity_required: float = Field(gt=0)


class MenuItemRecipeUpdate(BaseModel):
    entries: list[RecipeEntryPayload] = Field(min_length=1)


class MenuItemRecipeResponse(OrmBase):
    menu_item_id: int
    inventory_item_id: int
    quantity_required: float
    created_at: datetime
    updated_at: datetime


class InventoryItemResponse(OrmBase):
    restaurant_id: int
    name: str
    unit: str
    quantity_available: float
    minimum_quantity: float
    created_at: datetime
    updated_at: datetime
