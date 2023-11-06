import os
import pymongo
import requests
import json
from bson import ObjectId

# Fetch mongo env vars
usr = os.environ['MONGO_DB_USER']
pwd = os.environ['MONGO_DB_PASS']
mongo_db_name = os.environ['MONGO_DB_NAME']
mongo_collection_name = os.environ['MONGO_COLLECTION_NAME2']
url = os.environ['MONGO_DB_URL']

# Connection String
client = pymongo.MongoClient("mongodb+srv://" + usr + ":" + pwd + "@" + url + "/test?retryWrites=true&w=majority")
db = client[mongo_db_name]
collection = db[mongo_collection_name]

# Colección adicional para el contador
counter_collection = db['LambdaExecutionCounter']

# Convertir ObjectId a string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def lambda_handler(event, context):
    # Obtener el contador actual de ejecuciones
    counter = counter_collection.find_one({"_id": "dweetCounter"})
    
    if counter:
        current_count = counter.get("count", 0)
    else:
        # Inicializar contador si no existe
        counter_collection.insert_one({"_id": "dweetCounter", "count": 0})
        current_count = 0

    # Si el contador es 14 (0-indexed, por lo que es la 15ª ejecución), resetea el contador y envía al webhook
    if current_count == 14:
        counter_collection.update_one({"_id": "dweetCounter"}, {"$set": {"count": 0}})
        send_to_webhook()
    else:
        # Incrementa el contador
        counter_collection.update_one({"_id": "dweetCounter"}, {"$inc": {"count": 1}})

    # Consultar la página para obtener los datos
    page_url = "https://dweet.io:443/get/dweets/for/thecore"
    response_page = requests.get(page_url)

    data = response_page.json()

    # Verificar si la respuesta tiene dweets y tomar el más reciente
    latest_dweet = data.get('with', [{}])[0]

    # Extraer los datos de content
    content_data = latest_dweet.get('content', {})
    temperature = content_data.get('temperature')
    humidity = content_data.get('humidity')

    # Insertar los datos en MongoDB
    collection.insert_one({
        'timestamp': latest_dweet.get('created'),
        'temperature': temperature,
        'humidity': humidity
    })

    return {
        "statusCode": 200,
        "body": "Data processed successfully."
    }

def send_to_webhook():
    # Recuperar todos los datos de la base de datos
    items = list(collection.find())
    
    # Convert the items (containing ObjectIds) into a Python object
    items_obj = convert_items_to_serializable_obj(items)

    # Enviar los datos al webhook
    webhook_url = "https://webhook.site/aa88b3ad-be3e-475f-8adc-f5dc99559dc1"
    requests.post(webhook_url, json=items_obj)

def convert_items_to_serializable_obj(items):
    result = []
    for item in items:
        item_dict = {}
        for key, value in item.items():
            if isinstance(value, ObjectId):
                item_dict[key] = str(value)
            else:
                item_dict[key] = value
        result.append(item_dict)
    return result
