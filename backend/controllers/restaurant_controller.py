from factory import api
from flask import Blueprint
from flask_jwt_extended import current_user, get_jwt, jwt_required
from spectree import Response

from models import Restaurant
from models.restaurant import RestaurantResponse
from utils.response_schema import GenericResponse

restaurant_controller = Blueprint(
    "restaurant_controller", __name__, url_prefix="/restaurants"
)


@restaurant_controller.get("/me")
@api.validate(
    resp=Response(
        HTTP_200=RestaurantResponse,
        HTTP_403=GenericResponse,
        HTTP_404=GenericResponse,
    ),
    tags=["restaurants"],
)
@jwt_required()
def get_restaurant():
    """
    Get logged restaurant.
    """

    if get_jwt().get("account_type") != "restaurant" or not isinstance(
        current_user, Restaurant
    ):
        return {"msg": "Restaurant token required."}, 403

    response = RestaurantResponse.model_validate(current_user).to_response_dict()

    return response, 200
