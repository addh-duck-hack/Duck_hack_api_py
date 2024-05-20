from fastapi import APIRouter, Depends, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime
import pytz
from bson import ObjectId
from app.db.models.user import Device
from app.db.client import db_client
from app.db.models.product import Product
from app.db.schemas.product import products_schema
from app.routers.auth_api import validate_token, search_user, new_device, exception_401

router = APIRouter(prefix="/products",
                   tags=["Servicios dedicados a los prodcutos"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No disponible"}})



@router.get("/", response_model=list[Product], status_code=status.HTTP_200_OK)
async def get():
    products = db_client.products.aggregate([
        {
            "$lookup": {
                "from": "product_images",
                "localField": "sku",
                "foreignField": "sku",
                "as": "images"
            }
        }
    ])

    return products_schema(products)
