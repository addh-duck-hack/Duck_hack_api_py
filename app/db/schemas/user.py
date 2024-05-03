### User schema ###
def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "full_name": user["full_name"],
            "phone": user["phone"],
            "email": user["email"],
            "password": user["password"],
            "disabled": user["disabled"]}

def users_schema(users) -> list:
    return [user_schema(user) for user in users]


### Convertir registro de la base en diccionario ###
def device_schema(device) -> dict:
    return {
        "id": str(device["_id"]),
        "token": device["token"],
        "uuid": device["uuid"],
        "exp": device["exp"],
        "user_id": device["user_id"]}

def session_schema(session) -> dict:
    return {
        "id": str(session["_id"]),
        "token": session["token"],
        "date": session["date"],
        "uuid": session["uuid"],
        "exp": session["exp"],
        "user_id": str(session["user_id"])}