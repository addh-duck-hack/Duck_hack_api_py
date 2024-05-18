from fastapi import FastAPI
from app.routers import users, auth_api
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(users.router)
app.include_router(auth_api.router)


@app.get("/")
async def root():
    return "El servicio esta en funcionamiento"
