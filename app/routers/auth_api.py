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

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 24
SECRET = "b9ec9a97d47715d921f35b9af80dabd67a301de0"


router = APIRouter(prefix="/auth",
                   tags=["Autenticacion de dispositivos y usuarios al API"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No disponible"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

crypt = CryptContext(schemes=["bcrypt"])

#Helpers
def search_device(field: str, key: str):
    try:
        device = db_client.devices.find_one({field: key})
        return Device(**device_schema(device))
    except:
        return {"error": "No se ha encontrado el dispositivo"}

def search_user(field: str, key):
    try:
        user = db_client.users.find_one({field: key})
        return User(**user_schema(user))
    except:
        return {"error": "No se ha encontrado el usuario"}
    
def search_session(id: str):
    try:
        session = db_client.sessions.find_one({"_id": ObjectId(id)})
        return Session(**session_schema(session))
    except:
        return {"error": "No se encontro la sesion"}
    
def new_device(uuid: str, user_id: str):
    expiration = datetime.now(pytz.timezone("America/Mexico_City")) + timedelta(hours=ACCESS_TOKEN_DURATION)
    expiration_format = expiration.strftime('%d/%m/%Y %H:%M')
    access_token = {
        "exp": expiration,
        "uuid": uuid,
        "exp_format": expiration_format        
    }

    return {"token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "uuid": uuid,
            "exp": expiration_format,
            "user_id": user_id}

def create_session(user_id: str, uuid: str) -> str:
    date_format = datetime.now(pytz.timezone("America/Mexico_City")).strftime('%d/%m/%Y %H:%M')
    expiration = datetime.now(pytz.timezone("America/Mexico_City")) + timedelta(hours=ACCESS_TOKEN_DURATION)
    expiration_format = expiration.strftime('%d/%m/%Y %H:%M')
    access_token = {
        "exp": expiration,
        "user_id": user_id,
        "exp_format": expiration_format        
    }

    new_session = {
        "token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "date": date_format,
        "uuid": uuid,
        "exp": expiration_format,
        "user_id": ObjectId(user_id)
    }
    return db_client.sessions.insert_one(new_session).inserted_id

def exception_401(error: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= error,
        headers={"WWW-Authenticate": "Bearer"})        

# Auth
async def validate_token(token: Annotated[str, Depends(oauth2)]):
    try:
        uuid = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("uuid")
        exp_format = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("exp_format")
        if uuid is None:
            raise exception_401("Credenciales de autenticación inválidas")
        current_date = datetime.now(pytz.timezone("America/Mexico_City")).strftime('%d/%m/%Y %H:%M')
        current_date = datetime.strptime(current_date, '%d/%m/%Y %H:%M')
        old_date = datetime.strptime(exp_format, '%d/%m/%Y %H:%M')
        if current_date > old_date:
            print("Token vencido no puede ingresar con ese token")
            raise exception_401("El token vencio, favor de cerrar y abrir la aplicación")
    except JWTError:
        raise exception_401("No se pudieron validar las credenciales")
    return search_device("uuid", uuid)

# Service token
@router.post("/token", response_model=Device, status_code=status.HTTP_200_OK)
async def validate_device(request: RequestAuth):
    print(f"UUID recibido {request.uuid}")
    old_auth = search_device(field="uuid", key= request.uuid)
    if type(old_auth) == Device:
        current_date = datetime.now(pytz.timezone("America/Mexico_City")).strftime('%d/%m/%Y %H:%M')
        current_date = datetime.strptime(current_date, '%d/%m/%Y %H:%M')
        old_date = datetime.strptime(old_auth.exp, '%d/%m/%Y %H:%M')
        if current_date > old_date:
            print("Token vencido se otorga uno nuevo")
            device = new_device(request.uuid, "")
            db_client.devices.find_one_and_replace({"_id": ObjectId(old_auth.id)},device)
            return search_device(field="_id", key= ObjectId(old_auth.id))
        else:
            print("Token vigente")
            return old_auth
    print("No existe token para este ID, se otorga uno nuevo")
    device = new_device(request.uuid, "")
    id_device = db_client.devices.insert_one(device).inserted_id
    return search_device(field="_id", key= ObjectId(id_device))

# Service Login
@router.post("/login")
async def login(form: RequestLogin, current_device: Annotated[Device, Depends(validate_token)]):
    user:User
    known_device = False
    # Si se intenta logear con faceID validamos que el dispositivo este asociado a una cuenta
    if form.face_id:
        if current_device.user_id == "":
            raise exception_401("El dispositivo no puede iniciar con FaceID, favor de ingresar usuario y contraseña")
        else:
            print("El dispositivo esta autenticado para usar FaceID")
            user = search_user("_id",ObjectId(current_device.user_id))
            known_device = True
    else:
        # Recuperamos usuario por el telefono y validamos la contraseña
        user = search_user("phone",form.phone)
        if not type(user) == User:
            raise exception_401("Credenciales incorrectas")
        if not crypt.verify(form.password, user.password):
            raise exception_401("Credenciales incorrectas")

    id_session = create_session(user.id, current_device.uuid)
    session = search_session(id_session)
    if not known_device:
        device = new_device(current_device.uuid, user.id)
        db_client.devices.find_one_and_replace({"_id": ObjectId(current_device.id)},device)

    return {"user": user, "session": session}