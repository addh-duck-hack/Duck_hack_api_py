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
from app.db.models.user import Device, User
from app.db.schemas.user import users_schema
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
        current_date = datetime.now(pytz.timezone("America/Mexico_City")).strftime('%d/%m/%Y %H:%M')
        current_date = datetime.strptime(current_date, '%d/%m/%Y %H:%M')
        old_date = datetime.strptime(exp_format, '%d/%m/%Y %H:%M')
        if current_date > old_date:
            print("Token vencido el telefono tendria que controlar el vencimiento del token de sesion")
            raise exception_401("El token vencio, por favor vuelve a iniciar sesion")
    except JWTError:
        raise exception_401("No se pudieron validar las credenciales")
    return search_user("_id", ObjectId(user_id))

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
@router.put("/", response_model=User, status_code=status.HTTP_200_OK)
async def edit(user: User, current_user: Annotated[Device, Depends(validate_session)]):
    #al llegar aqui ya tenemos al usuario del token, lo modificamos
    user_dict = dict(user)
    del user_dict["id"]
    user_dict["password"] = crypt.hash(user.password)

    db_client.users.find_one_and_replace({"_id": ObjectId(current_user.id)},user_dict)
    return search_user("_id", ObjectId(current_user.id))

# Servicio para traer todos los usuarios
@router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def get():
    return users_schema(db_client.users.find())