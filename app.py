from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
import re

MONGO_URI = "mongodb://mongodb:27017/"
client = MongoClient(MONGO_URI)
db = client['car_db']
cars_collection = db['cars']

def seed_data():
    # CARS_DATA is now defined inside seed_data
    CARS_DATA_TO_SEED = [
        { # Parsable performance
            "id": 1,
            "brand": "Honda",
            "model": "Civic Type R", # Made it more sporty
            "year": 2023,
            "price": 43000,
            "style": "Hot Hatch",
            "performance": "0-60mph in 5.3s, Track-focused handling",
            "wheel_drive": "FWD",
            "sales": "High demand among enthusiasts",
            "after_sales": "3-year/36,000-mile warranty",
            "fuel_efficiency": "22 MPG City / 28 MPG Hwy",
            "safety": "Advanced safety suite, Strong chassis",
            "color": "Championship White, Rallye Red, Boost Blue",
            "energy": "Gasoline",
            "engine_hp": 315,
            "mileage": 8 
        },
        { # Non-parsable performance
            "id": 2,
            "brand": "Toyota",
            "model": "RAV4 Hybrid", # Specified Hybrid
            "year": 2023,
            "price": 31000,
            "style": "SUV",
            "performance": "Smooth and efficient powertrain, Excellent for city driving", # Non-parsable
            "wheel_drive": "AWD",
            "sales": "Extremely popular hybrid SUV",
            "after_sales": "2-year/25,000-mile ToyotaCare, 10-year/150,000-mile hybrid battery warranty",
            "fuel_efficiency": "41 MPG City / 38 MPG Hwy",
            "safety": "NHTSA 5-Star Overall, Toyota Safety Sense 2.5+",
            "color": "Silver Sky Metallic, Magnetic Gray Metallic, Blueprint",
            "energy": "Hybrid",
            "engine_hp": 219, # Combined HP
            "mileage": 12
        },
        { # Parsable performance (different format)
            "id": 3,
            "brand": "Ford",
            "model": "Mustang Mach-E GT", # Specified GT
            "year": 2023,
            "price": 60000,
            "style": "Electric SUV",
            "performance": "Hits 60mph in just 3.8 seconds!", # Parsable, different format
            "wheel_drive": "AWD",
            "sales": "Performance EV with strong appeal",
            "after_sales": "3-year/36,000-mile bumper-to-bumper, 8-year/100,000-mile battery warranty",
            "fuel_efficiency": "EPA-estimated 270 miles range (GT)",
            "safety": "IIHS Top Safety Pick, Ford Co-Pilot360 Active 2.0",
            "color": "Cyber Orange Metallic, Grabber Blue Metallic, Star White Metallic",
            "energy": "Electric",
            "engine_hp": 480, # GT Performance Edition
            "mileage": 6
        },
        { # Parsable performance (another variation)
            "id": 4,
            "brand": "Chevrolet",
            "model": "Corvette Stingray", # Changed model for performance
            "year": 2023,
            "price": 68000, 
            "style": "Sports Car",
            "performance": "Mid-engine marvel, 0-60 mph in 2.9s with Z51 package", # Parsable
            "wheel_drive": "RWD",
            "sales": "Iconic American sports car, High demand",
            "after_sales": "3-year/36,000-mile warranty, Specialized service available",
            "fuel_efficiency": "16 MPG City / 24 MPG Hwy",
            "safety": "High-performance brakes, Advanced traction control",
            "color": "Torch Red, Accelerate Yellow Metallic, Hypersonic Gray Metallic",
            "energy": "Gasoline",
            "engine_hp": 495, # With performance exhaust
            "mileage": 3
        }
    ]
    if cars_collection.count_documents({}) == 0:
        print("Seeding initial car data into MongoDB...")
        for car_data in CARS_DATA_TO_SEED: # Use the local list here
            cars_collection.insert_one(car_data.copy())
        print("Data seeding complete.")
    else:
        print("Car data already exists in MongoDB. Skipping seed.")

def process_car_data(car_doc):
    performance_string = car_doc.get('performance', '')
    match = re.search(r"(\d+\.?\d*)\s*s", performance_string) # searches for digits followed by 's' (like 4.5s)
    performance_metric = float(match.group(1)) if match else None

    processed_car = {
        "id": str(car_doc["_id"]), # String version of MongoDB's ObjectId
        "original_id": car_doc.get("id"), # Original integer ID, if used
        "brand": car_doc.get("brand"),
        "model": car_doc.get("model"),
        "year": car_doc.get("year"),
        "price": car_doc.get("price"),
        "style": car_doc.get("style"),
        "performance": performance_string, # Keep original string
        "performance_metric": performance_metric, # Add new numerical metric
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
    return processed_car

app = Flask(__name__)

# CARS_DATA list is removed as data is now in MongoDB

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/cars', methods=['GET'])
def get_all_cars():
    filter_query = {}

    # Process brand filter
    brand = request.args.get('brand')
    if brand:
        filter_query['brand'] = {'$regex': brand, '$options': 'i'}

    # Process style filter
    style = request.args.get('style')
    if style:
        filter_query['style'] = {'$regex': style, '$options': 'i'}

    # Process price filters
    price_min_str = request.args.get('price_min')
    price_max_str = request.args.get('price_max')
    price_conditions = {}

    if price_min_str:
        try:
            price_conditions['$gte'] = int(price_min_str)
        except ValueError:
            # Silently ignore if not a valid int, or log an error
            # app.logger.warning(f"Invalid price_min value: {price_min_str}")
            pass 
    if price_max_str:
        try:
            price_conditions['$lte'] = int(price_max_str)
        except ValueError:
            # Silently ignore if not a valid int, or log an error
            # app.logger.warning(f"Invalid price_max value: {price_max_str}")
            pass
            
    if price_conditions:
        filter_query['price'] = price_conditions
    
    car_list = []
    # Fetch from MongoDB with filters and sort
    for car_doc in cars_collection.find(filter_query).sort([("id", 1)]):
        car_list.append(process_car_data(car_doc)) # Use helper function
    return jsonify(car_list)

@app.route('/api/cars/<string:car_id_str>', methods=['GET'])
def get_car_by_id(car_id_str):
    try:
        object_id_to_find = ObjectId(car_id_str)
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400

    car_doc = cars_collection.find_one({"_id": object_id_to_find})

    if car_doc:
        return jsonify(process_car_data(car_doc)) # Use helper function
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
            selected_cars.append(process_car_data(car_doc)) # Use helper function
            
    return render_template('compare.html', cars=selected_cars)

@app.route('/add', methods=['GET', 'POST'])
def add_car_route():
    if request.method == 'POST':
        # --- Data Retrieval ---
        brand = request.form.get('brand')
        model = request.form.get('model')
        try:
            year = int(request.form.get('year'))
            price = int(request.form.get('price'))
            engine_hp_str = request.form.get('engine_hp')
            mileage_str = request.form.get('mileage')
            
            engine_hp = int(engine_hp_str) if engine_hp_str and engine_hp_str.strip() else None
            mileage = int(mileage_str) if mileage_str and mileage_str.strip() else None
        except ValueError:
            # Basic error handling: return an error message or re-render form with error
            # For now, a simple error, but flashing messages would be better in a real app.
            return "Invalid data for year, price, engine_hp, or mileage. Please enter numbers.", 400

        style = request.form.get('style')
        performance = request.form.get('performance')
        wheel_drive = request.form.get('wheel_drive')
        sales = request.form.get('sales')
        after_sales = request.form.get('after_sales')
        fuel_efficiency = request.form.get('fuel_efficiency')
        safety = request.form.get('safety')
        color = request.form.get('color')
        energy = request.form.get('energy')

        # --- Basic Validation (ensure required fields are present) ---
        if not all([brand, model, year is not None, price is not None]): # year and price are converted, so check not None
            return "Required fields (Brand, Model, Year, Price) are missing or invalid.", 400

        # --- Generate new integer id ---
        # Find the car with the highest current 'id' in cars_collection
        last_car_doc = cars_collection.find_one(sort=[("id", -1)])
        new_id = (last_car_doc["id"] + 1) if last_car_doc and "id" in last_car_doc else 1
        
        # --- Create new car data dictionary ---
        new_car_data = {
            "id": new_id, # Our custom integer ID
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "style": style,
            "performance": performance,
            "wheel_drive": wheel_drive,
            "sales": sales,
            "after_sales": after_sales,
            "fuel_efficiency": fuel_efficiency,
            "safety": safety,
            "color": color,
            "energy": energy,
            "engine_hp": engine_hp,
            "mileage": mileage
        }

        # --- Insert into MongoDB ---
        cars_collection.insert_one(new_car_data)
        
        return redirect(url_for('home')) 

    # --- Handle GET request ---
    return render_template('add_car.html')

if __name__ == '__main__':
    seed_data() # Call seeding function
    app.run(debug=True, host='0.0.0.0')
