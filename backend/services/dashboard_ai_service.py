import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median


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


@dataclass(frozen=True)
class DeliveryRecord:
    order_id: str
    order_time: datetime
    main_dish: str
    order_price: float
    delivery_neighborhood: str
    weather: str
    traffic_level: str
    restaurant_busy_level: str
    courier_vehicle: str
    delivery_time_minutes: int

    @property
    def order_date(self) -> date:
        return self.order_time.date()

    @property
    def order_period(self) -> str:
        hour = self.order_time.hour
        if 5 <= hour <= 10:
            return "morning"
        if 11 <= hour <= 14:
            return "lunch"
        if 15 <= hour <= 17:
            return "afternoon"
        if 18 <= hour <= 22:
            return "dinner"
        return "late_night"


class DashboardAIService:
    def __init__(self):
        backend_dataset_path = (
            Path(__file__).resolve().parents[1] / "datasets" / "deliveries_train.csv"
        )
        notebook_dataset_path = (
            Path(__file__).resolve().parents[2] / "ia" / "datasets" / "deliveries_train.csv"
        )
        self.dataset_path = (
            backend_dataset_path if backend_dataset_path.exists() else notebook_dataset_path
        )
        self._cache_mtime = None
        self._records: list[DeliveryRecord] = []

    def _load_records(self) -> list[DeliveryRecord]:
        current_mtime = self.dataset_path.stat().st_mtime
        if self._cache_mtime == current_mtime and self._records:
            return self._records

        records: list[DeliveryRecord] = []
        with self.dataset_path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append(
                    DeliveryRecord(
                        order_id=row["order_id"],
                        order_time=datetime.fromisoformat(row["order_time"]),
                        main_dish=row["main_dish"],
                        order_price=float(row["order_price"]),
                        delivery_neighborhood=row["delivery_neighborhood"],
                        weather=row["weather"],
                        traffic_level=row["traffic_level"],
                        restaurant_busy_level=row["restaurant_busy_level"],
                        courier_vehicle=row["courier_vehicle"],
                        delivery_time_minutes=int(row["delivery_time_minutes"]),
                    )
                )

        self._records = records
        self._cache_mtime = current_mtime
        return records

    def _resolve_range(
        self,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> tuple[date, date, date]:
        records = self._load_records()
        reference_date = max(record.order_date for record in records)

        if start_date and end_date:
            return (
                date.fromisoformat(start_date),
                date.fromisoformat(end_date),
                date.fromisoformat(end_date),
            )

        if period == "today":
            return reference_date, reference_date, reference_date

        if period == "last_30_days":
            return reference_date - timedelta(days=29), reference_date, reference_date

        # Default and "last_7_days"
        return reference_date - timedelta(days=6), reference_date, reference_date

    def _filter_records(self, start: date, end: date) -> list[DeliveryRecord]:
        records = self._load_records()
        return [record for record in records if start <= record.order_date <= end]

    def _build_revenue_by_day(self, records: list[DeliveryRecord]) -> list[dict]:
        revenue_by_day: dict[date, float] = defaultdict(float)
        for record in records:
            revenue_by_day[record.order_date] += record.order_price

        chart = []
        for current_date in sorted(revenue_by_day):
            chart.append(
                {
                    "date": current_date.isoformat(),
                    "label": DAY_LABELS[current_date.weekday()],
                    "value": round(revenue_by_day[current_date], 2),
                    "valueCents": int(round(revenue_by_day[current_date] * 100)),
                }
            )

        return chart

    def _build_orders_by_period(self, records: list[DeliveryRecord]) -> list[dict]:
        counter: Counter[str] = Counter(record.order_period for record in records)
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

    def _build_top_dishes(self, records: list[DeliveryRecord], limit: int = 4) -> list[dict]:
        counter: Counter[str] = Counter(record.main_dish for record in records)
        top_items = counter.most_common(limit)
        return [
            {
                "label": dish.replace("_", " ").title(),
                "value": count,
            }
            for dish, count in top_items
        ]

    def _generate_insights(
        self,
        all_records: list[DeliveryRecord],
        filtered_records: list[DeliveryRecord],
        reference_records: list[DeliveryRecord],
    ) -> list[dict]:
        if not filtered_records:
            return [
                {
                    "title": "Sem dados suficientes",
                    "text": "Nao foi possivel gerar insight com o filtro atual.",
                    "severity": "neutral",
                    "confidence": 0.0,
                }
            ]

        overall_median = median(record.delivery_time_minutes for record in all_records)
        period_counter = Counter(record.order_period for record in filtered_records)
        top_period, top_period_orders = period_counter.most_common(1)[0]
        top_period_share = top_period_orders / max(len(filtered_records), 1)

        weather_counter = Counter(record.weather for record in reference_records or filtered_records)
        dominant_weather, dominant_weather_orders = weather_counter.most_common(1)[0]
        dominant_weather_times = [
            record.delivery_time_minutes
            for record in all_records
            if record.weather == dominant_weather
        ]
        dominant_weather_median = median(dominant_weather_times)
        weather_gap = max(dominant_weather_median - overall_median, 0)

        traffic_counter = Counter(
            record.traffic_level for record in reference_records or filtered_records
        )
        dominant_traffic, dominant_traffic_orders = traffic_counter.most_common(1)[0]
        dominant_traffic_times = [
            record.delivery_time_minutes
            for record in all_records
            if record.traffic_level == dominant_traffic
        ]
        dominant_traffic_median = median(dominant_traffic_times)
        traffic_gap = max(dominant_traffic_median - overall_median, 0)

        insights = [
            {
                "title": f"Reforce o periodo de {PERIOD_LABELS[top_period].lower()}",
                "text": (
                    f"{int(round(top_period_share * 100))}% dos pedidos do recorte atual "
                    f"acontecem em {PERIOD_LABELS[top_period].lower()}. "
                    "Ajuste equipe e mise en place para esse pico."
                ),
                "severity": "green" if top_period_share >= 0.4 else "orange",
                "confidence": round(min(max(top_period_share, 0.35), 0.95), 2),
                "source": "period_distribution",
            },
            {
                "title": f"Clima {dominant_weather} aumenta o risco operacional",
                "text": (
                    f"Nas entregas com clima {dominant_weather}, a mediana historica sobe para "
                    f"{int(round(dominant_weather_median))} min, contra {int(round(overall_median))} min no geral."
                ),
                "severity": "red" if weather_gap >= 10 else "orange",
                "confidence": round(min(max(weather_gap / 20, 0.4), 0.95), 2),
                "source": "weather_quartiles",
            },
            {
                "title": f"Transito {dominant_traffic} pede atencao",
                "text": (
                    f"Com transito {dominant_traffic}, a mediana historica de entrega fica em "
                    f"{int(round(dominant_traffic_median))} min. Reforce rotas e entregadores."
                ),
                "severity": "red" if traffic_gap >= 10 else "orange",
                "confidence": round(min(max(traffic_gap / 20, 0.35), 0.95), 2),
                "source": "traffic_analysis",
            },
        ]

        insights.sort(key=lambda item: item["confidence"], reverse=True)
        return insights

    def get_dashboard(self, period: str | None = None, start_date: str | None = None, end_date: str | None = None) -> dict:
        start, end, reference_date = self._resolve_range(period, start_date, end_date)
        all_records = self._load_records()
        filtered_records = self._filter_records(start, end)
        reference_records = [record for record in all_records if record.order_date == reference_date]

        if not reference_records:
            reference_records = filtered_records

        total_orders_today = len(reference_records)
        revenue_today = sum(record.order_price for record in reference_records)
        top_dish_counter = Counter(record.main_dish for record in reference_records)
        top_dish_name, top_dish_orders = top_dish_counter.most_common(1)[0]

        insights = self._generate_insights(all_records, filtered_records, reference_records)

        return {
            "restaurantId": None,
            "referenceDate": reference_date.isoformat(),
            "totalOrdersToday": total_orders_today,
            "revenueToday": round(revenue_today, 2),
            "revenueTodayCents": int(round(revenue_today * 100)),
            "topDishToday": {
                "name": top_dish_name.replace("_", " ").title(),
                "orders": top_dish_orders,
            },
            "revenueByDay": self._build_revenue_by_day(filtered_records),
            "ordersByPeriod": self._build_orders_by_period(filtered_records),
            "bestDishes": self._build_top_dishes(filtered_records),
            "aiInsight": insights[0],
            "generatedInsights": insights,
        }

    def get_ai_insights(self, period: str | None = None, start_date: str | None = None, end_date: str | None = None) -> dict:
        dashboard = self.get_dashboard(period=period, start_date=start_date, end_date=end_date)
        return {
            "referenceDate": dashboard["referenceDate"],
            "data": dashboard["generatedInsights"],
        }


dashboard_ai_service = DashboardAIService()
