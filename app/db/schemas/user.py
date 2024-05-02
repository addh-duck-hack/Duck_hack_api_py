### User schema ###
def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]}


def users_schema(users) -> list:
    return [user_schema(user) for user in users]


### Convertir registro de la base en diccionario ###
def device_schema(device) -> dict:
    return {
        "id": str(device["_id"]),
        "token": device["token"],
        "uuid": device["uuid"],
        "exp": device["exp"],
        "id_user": device["id_user"]}