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
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "price": 24000,
            "style": "Sedan",
            "performance": "0-60mph in 8.0s, Smooth ride",
            "wheel_drive": "FWD",
            "sales": "Very popular, High resale value",
            "after_sales": "3-year/36,000-mile warranty, Reliable service centers",
            "fuel_efficiency": "31 MPG City / 40 MPG Hwy",
            "safety": "IIHS Top Safety Pick+, Honda Sensing Suite",
            "color": "Meteorite Gray, Rallye Red, Aegean Blue",
            "energy": "Gasoline",
            "engine_hp": 158,
            "mileage": 10 
        },
        {
            "id": 2,
            "brand": "Toyota",
            "model": "RAV4",
            "year": 2023,
            "price": 28000,
            "style": "SUV",
            "performance": "0-60mph in 8.2s, Comfortable for families",
            "wheel_drive": "AWD optional",
            "sales": "Best-selling SUV",
            "after_sales": "2-year/25,000-mile ToyotaCare maintenance, Extensive dealer network",
            "fuel_efficiency": "27 MPG City / 35 MPG Hwy",
            "safety": "NHTSA 5-Star Overall, Toyota Safety Sense 2.5",
            "color": "Magnetic Gray Metallic, Blizzard Pearl, Blueprint",
            "energy": "Gasoline/Hybrid",
            "engine_hp": 203,
            "mileage": 15
        },
        {
            "id": 3,
            "brand": "Ford",
            "model": "Mustang Mach-E",
            "year": 2023,
            "price": 47000,
            "style": "Electric SUV",
            "performance": "0-60mph in 5.8s (Select), Instant torque",
            "wheel_drive": "RWD/AWD",
            "sales": "Growing EV market share",
            "after_sales": "3-year/36,000-mile bumper-to-bumper, 8-year/100,000-mile battery warranty",
            "fuel_efficiency": "EPA-estimated 314 miles range (Extended Range RWD)",
            "safety": "IIHS Top Safety Pick, Ford Co-Pilot360",
            "color": "Grabber Blue Metallic, Star White Metallic, Rapid Red Metallic",
            "energy": "Electric",
            "engine_hp": 266, # Base model, can go up to 480hp
            "mileage": 5
        },
        { # Keeping a 4th car as in original, updated to new structure
            "id": 4,
            "brand": "Chevrolet",
            "model": "Silverado 1500",
            "year": 2023,
            "price": 45000, # Adjusted for new structure context
            "style": "Pickup Truck",
            "performance": "Various engines available, Strong towing capacity",
            "wheel_drive": "RWD/4WD",
            "sales": "Popular full-size truck",
            "after_sales": "3-year/36,000-mile warranty, Wide service network",
            "fuel_efficiency": "Varies by engine (e.g., 2.7L Turbo: 19 MPG City / 22 MPG Hwy)",
            "safety": "Good crash test ratings, Available advanced safety features",
            "color": "Summit White, Black, Red Hot",
            "energy": "Gasoline/Diesel",
            "engine_hp": 310, # For 2.7L Turbo, other options exist
            "mileage": 20
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
            "brand": car_doc.get("brand"),
            "model": car_doc.get("model"),
            "year": car_doc.get("year"),
            "price": car_doc.get("price"),
            "style": car_doc.get("style"),
            "performance": car_doc.get("performance"),
            "wheel_drive": car_doc.get("wheel_drive"),
            "sales": car_doc.get("sales"),
            "after_sales": car_doc.get("after_sales"),
            "fuel_efficiency": car_doc.get("fuel_efficiency"),
            "safety": car_doc.get("safety"),
            "color": car_doc.get("color"),
            "energy": car_doc.get("energy"),
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
            "brand": car_doc.get("brand"),
            "model": car_doc.get("model"),
            "year": car_doc.get("year"),
            "price": car_doc.get("price"),
            "style": car_doc.get("style"),
            "performance": car_doc.get("performance"),
            "wheel_drive": car_doc.get("wheel_drive"),
            "sales": car_doc.get("sales"),
            "after_sales": car_doc.get("after_sales"),
            "fuel_efficiency": car_doc.get("fuel_efficiency"),
            "safety": car_doc.get("safety"),
            "color": car_doc.get("color"),
            "energy": car_doc.get("energy"),
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
