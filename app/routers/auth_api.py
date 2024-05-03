from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from app.db.models.user import Device
from app.db.client import db_client
from app.db.models.user import Device, RequestAuth, RequestLogin
from app.db.schemas.user import device_schema

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "b9ec9a97d47715d921f35b9af80dabd67a301de0"


router = APIRouter(prefix="/auth",
                   tags=["Autenticacion de dispositivos y usuarios al API"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No disponible"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

crypt = CryptContext(schemes=["bcrypt"])

#Helpers
def search_token(field: str, key: str):
    try:
        device = db_client.devices.find_one({field: key})
        return Device(**device_schema(device))
    except:
        return {"error": "No se ha encontrado el usuario"}
    
def new_device(uuid: str):
    expiration = datetime.now()
    expiration = expiration.strftime('%d/%m/%Y %H:%M')
    access_token = {
        "uuid": uuid,
        "exp": expiration
    }

    return {"token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "uuid": uuid,
            "exp": expiration,
            "id_user": ""}

# Auth
async def validate_token(token: Annotated[str, Depends(oauth2)]):
    print(token)
    return ""

# Service token
@router.post("/token", response_model=Device, status_code=status.HTTP_200_OK)
async def validate_device(request: RequestAuth):
    print(f"UUID recibido {request.uuid}")
    old_auth = search_token(field="uuid", key= request.uuid)
    if type(old_auth) == Device:
        current_date = datetime.now()
        print(current_date)
        old_date = datetime.strptime(old_auth.exp, '%d/%m/%Y %H:%M')
        print(old_date)
        if current_date > old_date:
            print("Token vencido se otrorga uno nuevo")
            device = new_device(request.uuid)
            print(device)
            db_client.devices.find_one_and_replace({"_id": ObjectId(old_auth.id)},device)
            return search_token(field="_id", key= ObjectId(old_auth.id))
        else:
            print("Token vigente se regresa")
            return old_auth
    print("No existe token para este ID, se otroga uno nuevo")
    device = new_device(request.uuid)
    id_device = db_client.devices.insert_one(device).inserted_id
    return search_token(field="_id", key= ObjectId(id_device))

# Service Login
@router.post("/login")
async def login(form: RequestLogin, current_user: Annotated[Device, Depends(validate_token)]):
    print(form)
    return current_user