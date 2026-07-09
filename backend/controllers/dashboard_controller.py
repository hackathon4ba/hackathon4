from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jwt, jwt_required
from pydantic import BaseModel
from spectree import Response

from factory import api
from models import Restaurant
from services.dashboard_ai_service import dashboard_ai_service
from utils.response_schema import GenericResponse

dashboard_controller = Blueprint(
    "dashboard_controller", __name__, url_prefix="/api/v1/restaurants"
)


class DashboardTopDish(BaseModel):
    name: str
    orders: int


class DashboardChartPoint(BaseModel):
    label: str
    value: int | float
    date: str | None = None
    period: str | None = None
    valueCents: int | None = None
    kind: str | None = None
    isForecast: bool | None = None


class AIInsightResponse(BaseModel):
    title: str
    text: str
    severity: str
    confidence: float
    source: str | None = None


class DashboardResponse(BaseModel):
    restaurantId: int
    referenceDate: str
    totalOrdersToday: int
    revenueToday: float
    revenueTodayCents: int
    topDishToday: DashboardTopDish
    revenueByDay: list[DashboardChartPoint]
    ordersByPeriod: list[DashboardChartPoint]
    bestDishes: list[DashboardChartPoint]
    aiInsight: AIInsightResponse


class AIInsightsEnvelope(BaseModel):
    referenceDate: str
    data: list[AIInsightResponse]


class PaginatedMeta(BaseModel):
    page: int
    pageSize: int
    total: int
    totalPages: int


class RevenueHistoryResponse(BaseModel):
    data: list[DashboardChartPoint]
    msg: str
    meta: PaginatedMeta


def _validate_restaurant_access(restaurant_id: int):
    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return {"msg": "Restaurant token required."}, 403

    if current_user.id != restaurant_id:
        return {"msg": "Restaurant access denied."}, 403

    return None


@dashboard_controller.get("/<int:restaurant_id>/dashboard")
@api.validate(
    resp=Response(
        HTTP_200=DashboardResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["dashboard"],
)
@jwt_required()
def get_dashboard(restaurant_id: int):
    """
    Return dashboard metrics and AI insight based on the dataset extracted from the notebook.
    """

    access_error = _validate_restaurant_access(restaurant_id)
    if access_error is not None:
        return access_error

    payload = dashboard_ai_service.get_dashboard(
        restaurant_id=restaurant_id,
        period=request.args.get("period"),
        start_date=request.args.get("startDate"),
        end_date=request.args.get("endDate"),
    )
    payload["restaurantId"] = restaurant_id
    payload.pop("generatedInsights", None)

    return payload, 200


@dashboard_controller.get("/<int:restaurant_id>/ai/insights")
@api.validate(
    resp=Response(
        HTTP_200=AIInsightsEnvelope,
        HTTP_403=GenericResponse,
    ),
    tags=["dashboard"],
)
@jwt_required()
def get_ai_insights(restaurant_id: int):
    """
    Return AI insights generated from the notebook dataset logic.
    """

    access_error = _validate_restaurant_access(restaurant_id)
    if access_error is not None:
        return access_error

    return (
        dashboard_ai_service.get_ai_insights(
            restaurant_id=restaurant_id,
            period=request.args.get("period"),
            start_date=request.args.get("startDate"),
            end_date=request.args.get("endDate"),
        ),
        200,
    )


@dashboard_controller.get("/<int:restaurant_id>/dashboard/revenue-history")
@api.validate(
    resp=Response(
        HTTP_200=RevenueHistoryResponse,
        HTTP_400=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["dashboard"],
)
@jwt_required()
def get_revenue_history(restaurant_id: int):
    access_error = _validate_restaurant_access(restaurant_id)
    if access_error is not None:
        return access_error

    page = request.args.get("page", default=1, type=int) or 1
    page_size = request.args.get("pageSize", default=10, type=int) or 10

    if page < 1 or page_size < 1:
        return {"msg": "Invalid pagination parameters."}, 400

    page_size = min(page_size, 100)
    payload = dashboard_ai_service.get_revenue_history(
        restaurant_id=restaurant_id,
        page=page,
        page_size=page_size,
    )

    return {
        "msg": "Revenue history fetched successfully.",
        "data": payload["data"],
        "meta": payload["meta"],
    }, 200
