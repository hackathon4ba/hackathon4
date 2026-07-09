from collections import Counter, defaultdict
from datetime import date, timedelta
from statistics import mean

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sqlalchemy import select
from torch.utils.data import DataLoader, TensorDataset

from factory import db
from models import Order, RevenueDaily
from services.revenue_daily_service import ensure_revenue_daily_for_restaurant


DAY_LABELS = {
    0: "Seg",
    1: "Ter",
    2: "Qua",
    3: "Qui",
    4: "Sex",
    5: "Sab",
    6: "Dom",
}

PERIOD_LABELS = {
    "morning": "Manha",
    "lunch": "Almoco",
    "afternoon": "Tarde",
    "dinner": "Jantar",
    "late_night": "Noite",
}

LOOK_BACK = 30
FORECAST_HORIZON = 7
HIDDEN_SIZE = 50
NUM_LAYERS = 2
LEARNING_RATE = 0.001
NUM_EPOCHS = 20
BATCH_SIZE = 32


class RevenueScaler:
    def __init__(self):
        self.minimum = 0.0
        self.maximum = 0.0

    def fit_transform(self, values: np.ndarray) -> np.ndarray:
        self.minimum = float(values.min()) if values.size else 0.0
        self.maximum = float(values.max()) if values.size else 0.0

        if self.maximum == self.minimum:
            return np.zeros_like(values, dtype=np.float32)

        return ((values - self.minimum) / (self.maximum - self.minimum)).astype(
            np.float32
        )

    def inverse_transform(self, values: np.ndarray) -> np.ndarray:
        if self.maximum == self.minimum:
            return np.full_like(values, fill_value=self.minimum, dtype=np.float32)

        return (values * (self.maximum - self.minimum) + self.minimum).astype(
            np.float32
        )


class ProductRNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int, num_layers: int = 1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
        out, _ = self.rnn(x, h0)
        out = self.fc(out[:, -1, :])
        return self.relu(out)


class DashboardAIService:
    def __init__(self):
        self._device = torch.device("cpu")
        self._forecast_cache: dict[tuple[int, int, str], list[dict]] = {}

    def _load_restaurant_orders(self, restaurant_id: int) -> list[Order]:
        query = select(Order).filter_by(restaurant_id=restaurant_id)
        return db.session.scalars(query.order_by(Order.created_at.asc())).all()

    def _resolve_range(
        self,
        reference_date: date,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> tuple[date, date, date]:
        if start_date and end_date:
            end = date.fromisoformat(end_date)
            return date.fromisoformat(start_date), end, end

        if period == "today":
            return reference_date, reference_date, reference_date

        if period == "last_30_days":
            return reference_date - timedelta(days=29), reference_date, reference_date

        return reference_date - timedelta(days=6), reference_date, reference_date

    def _filter_orders(self, orders: list[Order], start: date, end: date) -> list[Order]:
        return [order for order in orders if start <= order.created_at.date() <= end]

    def _load_revenue_rows(
        self,
        restaurant_id: int,
        start: date | None = None,
        end: date | None = None,
    ) -> list[RevenueDaily]:
        query = select(RevenueDaily).filter_by(restaurant_id=restaurant_id)
        if start is not None:
            query = query.where(RevenueDaily.revenue_date >= start)
        if end is not None:
            query = query.where(RevenueDaily.revenue_date <= end)

        return db.session.scalars(query.order_by(RevenueDaily.revenue_date.asc())).all()

    def _get_order_period(self, order: Order) -> str:
        hour = order.created_at.hour
        if 5 <= hour <= 10:
            return "morning"
        if 11 <= hour <= 14:
            return "lunch"
        if 15 <= hour <= 17:
            return "afternoon"
        if 18 <= hour <= 22:
            return "dinner"
        return "late_night"

    def _build_revenue_by_day(self, revenue_rows: list[RevenueDaily]) -> list[dict]:
        chart = []
        for revenue_row in revenue_rows:
            current_date = revenue_row.revenue_date
            value = revenue_row.revenue_cents / 100
            chart.append(
                {
                    "date": current_date.isoformat(),
                    "label": f"{DAY_LABELS[current_date.weekday()]} {current_date.day:02d}",
                    "value": round(value, 2),
                    "valueCents": revenue_row.revenue_cents,
                    "kind": "historical",
                    "isForecast": False,
                }
            )

        return chart

    def _combine_revenue_history_and_forecast(
        self,
        revenue_history: list[dict],
        revenue_projection: list[dict],
        reference_date: date,
    ) -> list[dict]:
        history_by_date = {
            item["date"]: {**item}
            for item in revenue_history
        }
        forecast_by_date = {
            item["date"]: item
            for item in revenue_projection
            if item["kind"] == "forecast"
        }

        chart: list[dict] = []
        for offset in range(-2, 1):
            current_date = reference_date + timedelta(days=offset)
            current_date_iso = current_date.isoformat()
            history_item = history_by_date.get(current_date_iso)
            if history_item is None:
                history_item = {
                    "date": current_date_iso,
                    "label": f"{DAY_LABELS[current_date.weekday()]} {current_date.day:02d}",
                    "value": 0.0,
                    "valueCents": 0,
                    "kind": "historical",
                    "isForecast": False,
                }

            history_item["kind"] = "current" if offset == 0 else "historical"
            history_item["isForecast"] = False
            chart.append(history_item)

        for step in range(1, FORECAST_HORIZON + 1):
            current_date = reference_date + timedelta(days=step)
            current_date_iso = current_date.isoformat()
            chart.append(
                forecast_by_date.get(
                    current_date_iso,
                    {
                        "date": current_date_iso,
                        "label": f"{DAY_LABELS[current_date.weekday()]} {current_date.day:02d}",
                        "value": 0.0,
                        "valueCents": 0,
                        "kind": "forecast",
                        "isForecast": True,
                    },
                )
            )

        return chart

    def _build_orders_by_period(self, orders: list[Order]) -> list[dict]:
        counter: Counter[str] = Counter(self._get_order_period(order) for order in orders)
        ordered_periods = ["morning", "lunch", "afternoon", "dinner", "late_night"]
        return [
            {
                "period": period,
                "label": PERIOD_LABELS[period],
                "value": counter.get(period, 0),
            }
            for period in ordered_periods
            if counter.get(period, 0) > 0
        ]

    def _build_top_dishes(self, orders: list[Order], limit: int = 4) -> list[dict]:
        counter: Counter[str] = Counter(order.main_dish for order in orders)
        return [{"label": dish, "value": count} for dish, count in counter.most_common(limit)]

    def _build_daily_product_revenue(
        self,
        orders: list[Order],
        reference_date: date,
    ) -> dict[str, np.ndarray]:
        if not orders:
            return {}

        rows = [
            {
                "date": order.created_at.date(),
                "main_dish": order.main_dish,
                "revenue": order.order_price_cents / 100,
            }
            for order in orders
        ]
        frame = pd.DataFrame(rows)
        grouped = (
            frame.groupby(["main_dish", "date"], as_index=False)["revenue"]
            .sum()
            .sort_values(["main_dish", "date"])
        )

        result: dict[str, np.ndarray] = {}
        for product in grouped["main_dish"].unique():
            product_df = grouped[grouped["main_dish"] == product].copy()
            min_date = product_df["date"].min()
            full_range = pd.date_range(start=min_date, end=reference_date, freq="D").date
            full_df = pd.DataFrame({"date": full_range})
            merged = pd.merge(full_df, product_df[["date", "revenue"]], on="date", how="left")
            merged["revenue"] = merged["revenue"].fillna(0.0)
            result[product] = merged["revenue"].to_numpy(dtype=np.float32)

        return result

    def _build_sequence_tensors(self, scaled_values: np.ndarray) -> tuple[torch.Tensor, torch.Tensor] | tuple[None, None]:
        features: list[np.ndarray] = []
        targets: list[np.ndarray] = []

        last_start = len(scaled_values) - LOOK_BACK - FORECAST_HORIZON + 1
        for index in range(max(last_start, 0)):
            features.append(scaled_values[index : index + LOOK_BACK])
            targets.append(
                scaled_values[
                    index + LOOK_BACK : index + LOOK_BACK + FORECAST_HORIZON
                ]
            )

        if not features or not targets:
            return None, None

        feature_tensor = torch.tensor(
            np.array(features, dtype=np.float32), dtype=torch.float32
        ).unsqueeze(-1)
        target_tensor = torch.tensor(np.array(targets, dtype=np.float32), dtype=torch.float32)
        return feature_tensor, target_tensor

    def _fallback_product_forecast(self, values: np.ndarray) -> np.ndarray:
        if values.size == 0:
            return np.zeros(FORECAST_HORIZON, dtype=np.float32)

        window = values[-min(7, len(values)) :]
        average = float(window.mean()) if window.size else 0.0
        return np.full(FORECAST_HORIZON, fill_value=max(0.0, average), dtype=np.float32)

    def _forecast_product_revenue(self, values: np.ndarray) -> np.ndarray:
        if len(values) < LOOK_BACK + FORECAST_HORIZON:
            return self._fallback_product_forecast(values)

        scaler = RevenueScaler()
        scaled_values = scaler.fit_transform(values)
        features, targets = self._build_sequence_tensors(scaled_values)
        if features is None or targets is None:
            return self._fallback_product_forecast(values)

        model = ProductRNN(
            input_size=1,
            hidden_size=HIDDEN_SIZE,
            output_size=FORECAST_HORIZON,
            num_layers=NUM_LAYERS,
        ).to(self._device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        dataset = TensorDataset(features.to(self._device), targets.to(self._device))
        loader = DataLoader(dataset, batch_size=min(BATCH_SIZE, len(dataset)), shuffle=True)

        model.train()
        for _ in range(NUM_EPOCHS):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

        latest_window = torch.tensor(
            scaled_values[-LOOK_BACK:].reshape(1, LOOK_BACK, 1),
            dtype=torch.float32,
            device=self._device,
        )

        model.eval()
        with torch.no_grad():
            prediction = model(latest_window).cpu().numpy().reshape(-1, 1)

        forecast = scaler.inverse_transform(prediction).reshape(-1)
        return np.clip(forecast, a_min=0.0, a_max=None)

    def _build_revenue_forecast_chart(
        self,
        restaurant_id: int,
        orders: list[Order],
        reference_date: date,
    ) -> list[dict]:
        if not orders:
            return []

        cache_key = (
            restaurant_id,
            len(orders),
            max(order.updated_at.isoformat() for order in orders),
        )
        cached = self._forecast_cache.get(cache_key)
        if cached is not None:
            return cached

        revenue_by_day: dict[date, float] = defaultdict(float)
        for order in orders:
            revenue_by_day[order.created_at.date()] += order.order_price_cents / 100

        product_revenue = self._build_daily_product_revenue(orders, reference_date)
        aggregated_forecast = np.zeros(FORECAST_HORIZON, dtype=np.float32)
        for values in product_revenue.values():
            aggregated_forecast += self._forecast_product_revenue(values)

        points: list[dict] = []
        for offset in range(-2, 1):
            current_date = reference_date + timedelta(days=offset)
            value = round(revenue_by_day.get(current_date, 0.0), 2)
            points.append(
                {
                    "date": current_date.isoformat(),
                    "label": f"{DAY_LABELS[current_date.weekday()]} {current_date.day:02d}",
                    "value": value,
                    "valueCents": int(round(value * 100)),
                    "kind": "current" if offset == 0 else "historical",
                    "isForecast": False,
                }
            )

        for step in range(FORECAST_HORIZON):
            current_date = reference_date + timedelta(days=step + 1)
            value = round(float(aggregated_forecast[step]), 2)
            points.append(
                {
                    "date": current_date.isoformat(),
                    "label": f"{DAY_LABELS[current_date.weekday()]} {current_date.day:02d}",
                    "value": value,
                    "valueCents": int(round(value * 100)),
                    "kind": "forecast",
                    "isForecast": True,
                }
            )

        stale_keys = [key for key in self._forecast_cache if key[0] == restaurant_id and key != cache_key]
        for key in stale_keys:
            self._forecast_cache.pop(key, None)

        self._forecast_cache[cache_key] = points
        return points

    def _generate_insights(
        self,
        all_orders: list[Order],
        filtered_orders: list[Order],
        reference_orders: list[Order],
        revenue_projection: list[dict],
    ) -> list[dict]:
        if not filtered_orders:
            return [
                {
                    "title": "Sem pedidos suficientes",
                    "text": "Ainda nao ha pedidos no banco para gerar insight operacional.",
                    "severity": "neutral",
                    "confidence": 0.0,
                    "source": "orders_database",
                }
            ]

        period_counter = Counter(self._get_order_period(order) for order in filtered_orders)
        top_period, top_period_orders = period_counter.most_common(1)[0]
        top_period_share = top_period_orders / max(len(filtered_orders), 1)

        delivered_orders = [order for order in filtered_orders if order.status == "delivered"]
        cancelled_orders = [order for order in filtered_orders if order.status == "cancelled"]
        cancelled_rate = len(cancelled_orders) / max(len(filtered_orders), 1)

        average_ticket = mean(order.order_price_cents / 100 for order in filtered_orders)
        reference_average_ticket = mean(order.order_price_cents / 100 for order in reference_orders)

        insights = [
            {
                "title": f"Reforce o periodo de {PERIOD_LABELS[top_period].lower()}",
                "text": (
                    f"{int(round(top_period_share * 100))}% dos pedidos do recorte atual "
                    f"acontecem em {PERIOD_LABELS[top_period].lower()}. "
                    "Ajuste equipe e preparo para esse pico."
                ),
                "severity": "green" if top_period_share >= 0.4 else "orange",
                "confidence": round(min(max(top_period_share, 0.35), 0.95), 2),
                "source": "orders_period_distribution",
            },
            {
                "title": "Acompanhe cancelamentos",
                "text": (
                    f"{int(round(cancelled_rate * 100))}% dos pedidos do recorte estao cancelados. "
                    "Revise gargalos de atendimento se esse percentual crescer."
                ),
                "severity": "red" if cancelled_rate >= 0.15 else "orange",
                "confidence": round(min(max(cancelled_rate * 3, 0.3), 0.9), 2),
                "source": "orders_status_mix",
            },
            {
                "title": "Monitore o ticket medio do dia",
                "text": (
                    f"O ticket medio do recorte esta em R$ {average_ticket:.2f} e o do dia de referencia "
                    f"esta em R$ {reference_average_ticket:.2f}."
                ),
                "severity": "green" if reference_average_ticket >= average_ticket else "orange",
                "confidence": 0.45,
                "source": "orders_revenue_analysis",
            },
        ]

        forecast_points = [point for point in revenue_projection if point["kind"] == "forecast"]
        current_points = [point for point in revenue_projection if point["kind"] == "current"]
        if forecast_points and current_points:
            current_value = current_points[0]["value"]
            future_average = mean(point["value"] for point in forecast_points)
            delta = future_average - current_value
            insights.append(
                {
                    "title": "Previsao de faturamento em 7 dias",
                    "text": (
                        f"O RNN projetou media diaria de R$ {future_average:.2f} para os proximos 7 dias, "
                        f"com variacao de R$ {delta:.2f} frente ao dia atual."
                    ),
                    "severity": "green" if delta >= 0 else "orange",
                    "confidence": 0.64,
                    "source": "rnn_revenue_forecast",
                }
            )

        if delivered_orders:
            delivered_share = len(delivered_orders) / max(len(filtered_orders), 1)
            insights.append(
                {
                    "title": "Volume entregue sustenta a operacao",
                    "text": (
                        f"{int(round(delivered_share * 100))}% dos pedidos do recorte estao entregues. "
                        "Use isso como referencia de estabilidade operacional."
                    ),
                    "severity": "green" if delivered_share >= 0.6 else "orange",
                    "confidence": round(min(max(delivered_share, 0.35), 0.9), 2),
                    "source": "orders_delivery_ratio",
                }
            )

        insights.sort(key=lambda item: item["confidence"], reverse=True)
        return insights

    def get_dashboard(
        self,
        restaurant_id: int,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        all_orders = self._load_restaurant_orders(restaurant_id)
        if not all_orders:
            empty_insight = self._generate_insights([], [], [], [])[0]
            return {
                "restaurantId": restaurant_id,
                "referenceDate": "",
                "totalOrdersToday": 0,
                "revenueToday": 0.0,
                "revenueTodayCents": 0,
                "topDishToday": {
                    "name": "Sem pedidos",
                    "orders": 0,
                },
                "revenueByDay": [],
                "ordersByPeriod": [],
                "bestDishes": [],
                "aiInsight": empty_insight,
                "generatedInsights": [empty_insight],
            }

        ensure_revenue_daily_for_restaurant(restaurant_id)
        reference_date = max(order.created_at.date() for order in all_orders)
        start, end, resolved_reference_date = self._resolve_range(
            reference_date=reference_date,
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

        filtered_orders = self._filter_orders(all_orders, start, end)
        reference_orders = [
            order for order in all_orders if order.created_at.date() == resolved_reference_date
        ]
        if not reference_orders:
            reference_orders = filtered_orders

        total_orders_today = len(reference_orders)
        revenue_today = sum(order.order_price_cents / 100 for order in reference_orders)
        top_dish_counter = Counter(order.main_dish for order in reference_orders)
        top_dish_name, top_dish_orders = (
            top_dish_counter.most_common(1)[0] if top_dish_counter else ("Sem pedidos", 0)
        )

        revenue_history = self._build_revenue_by_day(
            self._load_revenue_rows(restaurant_id, start=start, end=end)
        )
        revenue_projection = self._build_revenue_forecast_chart(
            restaurant_id=restaurant_id,
            orders=all_orders,
            reference_date=resolved_reference_date,
        )
        insights = self._generate_insights(
            all_orders,
            filtered_orders,
            reference_orders,
            revenue_projection,
        )
        revenue_chart = self._combine_revenue_history_and_forecast(
            revenue_history,
            revenue_projection,
            resolved_reference_date,
        )

        return {
            "restaurantId": restaurant_id,
            "referenceDate": resolved_reference_date.isoformat(),
            "totalOrdersToday": total_orders_today,
            "revenueToday": round(revenue_today, 2),
            "revenueTodayCents": int(round(revenue_today * 100)),
            "topDishToday": {
                "name": top_dish_name,
                "orders": top_dish_orders,
            },
            "revenueByDay": revenue_chart,
            "ordersByPeriod": self._build_orders_by_period(filtered_orders),
            "bestDishes": self._build_top_dishes(filtered_orders),
            "aiInsight": insights[0],
            "generatedInsights": insights,
        }

    def get_ai_insights(
        self,
        restaurant_id: int,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        dashboard = self.get_dashboard(
            restaurant_id=restaurant_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
        )
        return {
            "referenceDate": dashboard["referenceDate"],
            "data": dashboard["generatedInsights"],
        }

    def get_revenue_history(
        self,
        restaurant_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        ensure_revenue_daily_for_restaurant(restaurant_id)
        revenue_history = list(
            reversed(self._build_revenue_by_day(self._load_revenue_rows(restaurant_id)))
        )

        total = len(revenue_history)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "data": revenue_history[start:end],
            "meta": {
                "page": page,
                "pageSize": page_size,
                "total": total,
                "totalPages": total_pages,
            },
        }


dashboard_ai_service = DashboardAIService()
