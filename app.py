from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

MONGO_URI = "mongodb://mongodb:27017/"
client = MongoClient(MONGO_URI)
db = client['car_db']
cars_collection = db['cars']

def seed_data():
    # CARS_DATA is now defined inside seed_data
    CARS_DATA_TO_SEED = [
        {
            "id": 1,
            "make": "Toyota",
            "model": "Camry",
            "year": 2021,
            "price": 25000,
            "engine_hp": 203,
            "mileage": 15000
        },
        {
            "id": 2,
            "make": "Honda",
            "model": "Civic",
            "year": 2022,
            "price": 22000,
            "engine_hp": 158,
            "mileage": 12000
        },
        {
            "id": 3,
            "make": "Ford",
            "model": "Mustang",
            "year": 2020,
            "price": 35000,
            "engine_hp": 310,
            "mileage": 20000
        },
        {
            "id": 4,
            "make": "Chevrolet",
            "model": "Silverado",
            "year": 2023,
            "price": 45000,
            "engine_hp": 355,
            "mileage": 8000
        }
    ]
    if cars_collection.count_documents({}) == 0:
        print("Seeding initial car data into MongoDB...")
        for car_data in CARS_DATA_TO_SEED: # Use the local list here
            cars_collection.insert_one(car_data.copy())
        print("Data seeding complete.")
    else:
        print("Car data already exists in MongoDB. Skipping seed.")

app = Flask(__name__)

# CARS_DATA list is removed as data is now in MongoDB

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/cars', methods=['GET'])
def get_all_cars():
    car_list = []
    for car_doc in cars_collection.find():
        car_list.append({
            "id": str(car_doc["_id"]),
            "original_id": car_doc.get("id"), 
            "make": car_doc.get("make"),
            "model": car_doc.get("model"),
            "year": car_doc.get("year"),
            "price": car_doc.get("price"),
            "engine_hp": car_doc.get("engine_hp"),
            "mileage": car_doc.get("mileage")
        })
    return jsonify(car_list)

@app.route('/api/cars/<string:car_id_str>', methods=['GET'])
def get_car_by_id(car_id_str):
    try:
        object_id_to_find = ObjectId(car_id_str)
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400

    car_doc = cars_collection.find_one({"_id": object_id_to_find})

    if car_doc:
        transformed_car_doc = {
            "id": str(car_doc["_id"]),
            "original_id": car_doc.get("id"), 
            "make": car_doc.get("make"),
            "model": car_doc.get("model"),
            "year": car_doc.get("year"),
            "price": car_doc.get("price"),
            "engine_hp": car_doc.get("engine_hp"),
            "mileage": car_doc.get("mileage")
        }
        return jsonify(transformed_car_doc)
    else:
        return jsonify({"error": "Car not found"}), 404

@app.route('/compare')
def compare_cars():
    car_ids_str = request.args.get('ids')
    if not car_ids_str:
        return render_template('compare.html', cars=[])

    car_id_str_list = car_ids_str.split(',')
    selected_cars = []

    for id_str in car_id_str_list:
        try:
            object_id_to_find = ObjectId(id_str)
        except InvalidId:
            # Optionally, log this error or inform the user about invalid IDs
            print(f"Invalid ID format: {id_str}")
            continue 

        car_doc = cars_collection.find_one({"_id": object_id_to_find})
        if car_doc:
            selected_cars.append({
                "id": str(car_doc["_id"]),
                "original_id": car_doc.get("id"),
                "make": car_doc.get("make"),
                "model": car_doc.get("model"),
                "year": car_doc.get("year"),
                "price": car_doc.get("price"),
                "engine_hp": car_doc.get("engine_hp"),
                "mileage": car_doc.get("mileage")
            })
            
    return render_template('compare.html', cars=selected_cars)

if __name__ == '__main__':
    seed_data() # Call seeding function
    app.run(debug=True, host='0.0.0.0')
