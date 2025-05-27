from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

CARS_DATA = [
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/cars', methods=['GET'])
def get_all_cars():
    return jsonify(CARS_DATA)

@app.route('/api/cars/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    car = next((car for car in CARS_DATA if car["id"] == car_id), None)
    if car:
        return jsonify(car)
    else:
        return jsonify({"error": "Car not found"}), 404

@app.route('/compare')
def compare_cars():
    car_ids_str = request.args.get('ids')
    if not car_ids_str:
        # Or handle error appropriately
        return render_template('compare.html', cars=[])

    car_ids = [int(id_str) for id_str in car_ids_str.split(',')]
    
    selected_cars = []
    for car_id in car_ids:
        car = next((car for car in CARS_DATA if car["id"] == car_id), None)
        if car:
            selected_cars.append(car)
            
    return render_template('compare.html', cars=selected_cars)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
