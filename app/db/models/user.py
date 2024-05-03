from pydantic import BaseModel
from typing import Optional

class RequestAuth(BaseModel):
    uuid: str

class RequestLogin(BaseModel):
    phone: str
    password: str
    face_id: bool

class Device(BaseModel):
    id: str
    token: str
    uuid: str
    exp: str
    user_id: str

class User(BaseModel):
    id: str
    full_name: str
    phone: str
    email: str
    password: str
    disabled: bool

class Session(BaseModel):
    id: str
    token: str
    date: str
    uuid: str
    exp: str
    user_id: str