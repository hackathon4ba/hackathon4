from datetime import date

from sqlalchemy import func, select

from factory import db
from models import Order, RevenueDaily


def _normalize_date(value: date | str) -> date:
    if isinstance(value, date):
        return value

    return date.fromisoformat(value)


def sync_revenue_daily_for_date(
    restaurant_id: int,
    revenue_date: date | str,
    *,
    commit: bool = True,
):
    normalized_date = _normalize_date(revenue_date)
    revenue_date_sql = normalized_date.isoformat()

    revenue_cents, orders_count = db.session.execute(
        select(
            func.coalesce(func.sum(Order.order_price_cents), 0),
            func.count(Order.id),
        ).where(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) == revenue_date_sql,
        )
    ).one()

    entry = db.session.scalar(
        select(RevenueDaily).filter_by(
            restaurant_id=restaurant_id,
            revenue_date=normalized_date,
        )
    )

    if orders_count == 0:
        if entry is not None:
            db.session.delete(entry)
    elif entry is None:
        db.session.add(
            RevenueDaily(
                restaurant_id=restaurant_id,
                revenue_date=normalized_date,
                revenue_cents=int(revenue_cents or 0),
                orders_count=int(orders_count or 0),
            )
        )
    else:
        entry.revenue_cents = int(revenue_cents or 0)
        entry.orders_count = int(orders_count or 0)

    if commit:
        db.session.commit()


def sync_revenue_daily_for_dates(
    restaurant_id: int,
    revenue_dates: list[date | str] | tuple[date | str, ...] | set[date | str],
    *,
    commit: bool = True,
):
    normalized_dates = sorted({_normalize_date(revenue_date) for revenue_date in revenue_dates})
    if not normalized_dates:
        return

    for revenue_date in normalized_dates:
        sync_revenue_daily_for_date(restaurant_id, revenue_date, commit=False)

    if commit:
        db.session.commit()


def rebuild_revenue_daily_for_restaurant(restaurant_id: int, *, commit: bool = True):
    db.session.execute(
        db.delete(RevenueDaily).where(RevenueDaily.restaurant_id == restaurant_id)
    )

    rows = db.session.execute(
        select(
            func.date(Order.created_at).label("revenue_date"),
            func.coalesce(func.sum(Order.order_price_cents), 0).label("revenue_cents"),
            func.count(Order.id).label("orders_count"),
        )
        .where(Order.restaurant_id == restaurant_id)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at).asc())
    ).all()

    for revenue_date, revenue_cents, orders_count in rows:
        db.session.add(
            RevenueDaily(
                restaurant_id=restaurant_id,
                revenue_date=_normalize_date(revenue_date),
                revenue_cents=int(revenue_cents or 0),
                orders_count=int(orders_count or 0),
            )
        )

    if commit:
        db.session.commit()


def ensure_revenue_daily_for_restaurant(restaurant_id: int):
    order_count = db.session.scalar(
        select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)
    )
    if not order_count:
        return

    revenue_days_count = db.session.scalar(
        select(func.count(RevenueDaily.id)).where(RevenueDaily.restaurant_id == restaurant_id)
    )
    if revenue_days_count:
        return

    rebuild_revenue_daily_for_restaurant(restaurant_id)
