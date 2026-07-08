from factory import api, db
from sqlalchemy import select
from pydantic import BaseModel
from spectree import Response

from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from models import Restaurant, User
from models.restaurant import (
    RestaurantAuthResponse,
    RestaurantCreate,
    RestaurantLogin,
    RestaurantResponse,
)
from utils.response_schema import GenericResponse

auth_controller = Blueprint("auth_controller", __name__, url_prefix="/auth")


class LoginMessage(BaseModel):
    email: str
    password: str


class LoginResponseMessage(BaseModel):
    access_token: str


@auth_controller.post("/login")
@api.validate(
    json=LoginMessage,
    resp=Response(HTTP_200=LoginResponseMessage, HTTP_401=GenericResponse),
    tags=["auth"],
    security={},
)
def login():
    """
    Login in the system
    """

    data = request.json

    user = db.session.scalars(select(User).filter_by(email=data["email"])).first()

    if user and user.verify_password(data["password"]):
        return {
            "access_token": create_access_token(
                identity=user.email,
                additional_claims={"account_type": "user"},
                expires_delta=None,
            )
        }

    return {"msg": "Email and password do not match."}, 401


@auth_controller.post("/restaurants/register")
@api.validate(
    json=RestaurantCreate,
    resp=Response(
        HTTP_201=RestaurantAuthResponse,
        HTTP_400=GenericResponse,
        HTTP_409=GenericResponse,
    ),
    tags=["auth"],
    security={},
)
def register_restaurant():
    """
    Register a restaurant account.
    """

    data = request.json
    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if not name or not email or not password:
        return {"msg": "Name, email and password are required."}, 400

    if len(password) < 6:
        return {"msg": "Password must have at least 6 characters."}, 400

    existing_restaurant = db.session.scalars(
        select(Restaurant).filter_by(email=email)
    ).first()

    if existing_restaurant is not None:
        return {"msg": "Restaurant email already registered."}, 409

    restaurant = Restaurant(
        name=name,
        email=email,
        phone=data.get("phone"),
        address=data.get("address"),
        cuisine_type=data.get("cuisine_type"),
    )
    restaurant.password = password

    db.session.add(restaurant)
    db.session.commit()

    access_token = create_access_token(
        identity=restaurant.email,
        additional_claims={"account_type": "restaurant"},
        expires_delta=None,
    )

    return {
        "access_token": access_token,
        "restaurant": RestaurantResponse.model_validate(restaurant).to_response_dict(),
    }, 201


@auth_controller.post("/restaurants/login")
@api.validate(
    json=RestaurantLogin,
    resp=Response(
        HTTP_200=RestaurantAuthResponse,
        HTTP_401=GenericResponse,
        HTTP_403=GenericResponse,
    ),
    tags=["auth"],
    security={},
)
def login_restaurant():
    """
    Login a restaurant account.
    """

    data = request.json
    email = data["email"].strip().lower()

    restaurant = db.session.scalars(select(Restaurant).filter_by(email=email)).first()

    if restaurant and not restaurant.is_active:
        return {"msg": "Restaurant account is inactive."}, 403

    if restaurant and restaurant.verify_password(data["password"]):
        access_token = create_access_token(
            identity=restaurant.email,
            additional_claims={"account_type": "restaurant"},
            expires_delta=None,
        )

        return {
            "access_token": access_token,
            "restaurant": RestaurantResponse.model_validate(
                restaurant
            ).to_response_dict(),
        }

    return {"msg": "Email and password do not match."}, 401
