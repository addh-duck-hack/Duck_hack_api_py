from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import pytz
from bson import ObjectId
from app.db.models.user import Device
from app.db.client import db_client
from app.db.models.user import Device, RequestAuth, RequestLogin, User, Session
from app.db.schemas.user import device_schema, user_schema, session_schema
from app.routers.auth_api import validate_token, search_user, new_device, exception_401

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 24
SECRET = "b9ec9a97d47715d921f35b9af80dabd67a301de0"


router = APIRouter(prefix="/user",
                   tags=["Autenticacion de dispositivos y usuarios al API"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No disponible"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

crypt = CryptContext(schemes=["bcrypt"])

# Helpers
# Auth
async def validate_session(token: Annotated[str, Depends(oauth2)]):
    try:
        user_id = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("user_id")
        exp_format = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("exp_format")
        if user_id is None:
            raise exception_401("Credenciales de autenticación inválidas")
        current_date = datetime.now()
        old_date = datetime.strptime(exp_format, '%d/%m/%Y %H:%M')
        if current_date > old_date:
            print("Token vencido no puede ingresar con ese token")
            raise exception_401("El token vencio, favor de cerrar y abrir la aplicación")
    except JWTError:
        raise exception_401("No se pudieron validar las credenciales")
    return search_device("uuid", uuid)

# Servicio nuevo usuario
@router.post("/", response_model=User, status_code=status.HTTP_200_OK)
async def new(user: User, current_device: Annotated[Device, Depends(validate_token)]):
    print("El token se valido con exito")
    current_user = search_user("phone",user.phone)
    if type(current_user) == User:
        raise exception_401("El telefono ya se encuentra registrado")
    current_user = search_user("email",user.email)
    if type(current_user) == User:
        raise exception_401("El correo ya se encuentra registrado")

    user_dict = dict(user)
    del user_dict["id"]
    user_dict["password"] = crypt.hash(user.password)

    id_new_user = db_client.users.insert_one(user_dict).inserted_id
    new_user = search_user("_id",ObjectId(id_new_user))

    device = new_device(current_device.uuid, id_new_user)
    db_client.devices.find_one_and_replace({"_id": ObjectId(current_device.id)},device)

    return new_user

# Servicio modificar usuario
# @router.put("/", response_model=User, status_code=status.HTTP_200_OK)
# async def edit(user: User, current_device: Annotated[Device, Depends(validate_token)]):

@router.get("/")
async def edit():
    print(datetime.now(pytz.timezone("America/Mexico_City")))
    return ""