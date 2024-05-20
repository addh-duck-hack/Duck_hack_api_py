### Product schema ###

def product_characteristic_schema(product_characteristic) -> dict:
    return {
        "name": product_characteristic["name"],
        "value": product_characteristic["value"]
    }

def products_characteristic_schema(products_characteristic) -> list:
    return [product_characteristic_schema(product_characteristic) for product_characteristic in products_characteristic]

def product_characteristics_schema(product_characteristics) -> dict:
    return {
        "name": product_characteristics["name"],
        "characteristic": products_characteristic_schema(product_characteristics["characteristic"])
    }

def products_characteristics_schema(products_characteristics) -> list:
    return [product_characteristics_schema(product_characteristics) for product_characteristics in products_characteristics]

def product_image_schema(image) -> dict:
    return {
        "id": str(image["_id"]),
        "sku": image["sku"],
        "name": image["name"],
        "alt": image["alt"],
        "url": image["url"]
    }

def product_images_schema(images) -> list:
    return [product_image_schema(image) for image in images]

def product_schema(product) -> dict:
    return {"id": str(product["_id"]),
            "sku": product["sku"],
            "name": product["name"],
            "original_price": product["original_price"],
            "discount": product["discount"],
            "final_price": product["final_price"],
            "offer": product["offer"],
            "start_offer": product["start_offer"],
            "end_offer": product["end_offer"],
            "shipping_cost": product["shipping_cost"],
            "stock": product["stock"],
            "description": product["description"],
            "characteristics": products_characteristics_schema(product["characteristics"]),
            "delivery_terms": product["delivery_terms"],
            "images": product_images_schema(product["images"]),
            "registration_date": product["registration_date"],
            "disabled": product["disabled"],
            }

def products_schema(products) -> list:
    return [product_schema(product) for product in products]