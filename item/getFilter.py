import json
import os
import pymongo
import requests

# Fetch mongo env vars
usr = os.environ['MONGO_DB_USER']
pwd = os.environ['MONGO_DB_PASS']
mongo_db_name = os.environ['MONGO_DB_NAME']
mongo_collection_name = os.environ['MONGO_COLLECTION_NAME']
url = os.environ['MONGO_DB_URL']

# Connection String
client = pymongo.MongoClient("mongodb+srv://" + usr + ":" + pwd + "@" + url + "/test?retryWrites=true&w=majority")
db = client[mongo_db_name]
collection = db[mongo_collection_name]

def get(event, context):
    # Lee los parámetros desde el cuerpo de la solicitud
    body = json.loads(event['body'])
    currency_pair = body.get("currencyPair")
    date = body.get("date")

    # Buscar el ítem en la base de datos usando los criterios
    item = collection.find_one(
        {"data.currencyPair": currency_pair, "data.data.date": date},
        {"data.data.$": 1}
    )

    # Si el ítem no existe, devuelve un error 404
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Exchange rate not found for given criteria"})
        }

    # Convertir el ObjectID a string para que pueda ser serializado
    item["_id"] = str(item["_id"])

    # Si el item fue encontrado y tiene la fecha correcta, enviamos el exchangeRate al webhook
    if item and item["data"]["data"][0]["date"] == "2023-11-01":
        exchange_rate = item["data"]["data"][0]["exchangeRate"]
        payload = {"exchangeRate": exchange_rate}
        response_webhook = requests.post("https://webhook.site/aa88b3ad-be3e-475f-8adc-f5dc99559dc1", json=payload)

        # Puedes añadir una comprobación para ver si la solicitud fue exitosa
        if response_webhook.status_code != 200:
            print(f"Error al enviar datos al webhook. Código de estado: {response_webhook.status_code}")

    # Crear una respuesta y devolverla
    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    return response
