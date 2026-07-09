from datetime import date, datetime, timezone

from factory import db
from utils.response_schema import OrmBase


class RevenueDaily(db.Model):
    __tablename__ = "revenue_daily"
    __table_args__ = (
        db.UniqueConstraint(
            "restaurant_id", "revenue_date", name="uq_revenue_daily_restaurant_date"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), nullable=False, index=True
    )
    revenue_date = db.Column(db.Date, nullable=False, index=True)
    revenue_cents = db.Column(db.Integer, nullable=False, default=0)
    orders_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    restaurant = db.relationship("Restaurant", back_populates="daily_revenues")

    def __repr__(self) -> str:
        return (
            f"<RevenueDaily restaurant={self.restaurant_id} "
            f"date={self.revenue_date} revenue_cents={self.revenue_cents}>"
        )


class RevenueDailyResponse(OrmBase):
    restaurant_id: int
    revenue_date: date
    revenue_cents: int
    orders_count: int
    created_at: datetime
    updated_at: datetime

