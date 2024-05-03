from pydantic import BaseModel
from typing import Optional

class RequestAuth(BaseModel):
    uuid: str

class RequestLogin(BaseModel):
    phone: str
    password: str

class Device(BaseModel):
    id: str
    token: str
    uuid: str
    exp: str
    id_user: str

class User(BaseModel):
    id: Optional[str]
    username: str
    email: str
