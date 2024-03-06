from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Home"

@app.route('/points/standings', methods=['GET'])
def get_standing_points():
    data = {} 
    return jsonify(data)

@app.route('/points/entity', methods=['PATCH'])
def update_points():
    new_type = request.json
    return jsonify(new_type), 201
def remove_points():
    new_type = request.json
    return jsonify(new_type), 201

@app.route('/points/type', methods=['DELETE'])
def remove_type():
    new_type = request.json
    return jsonify(new_type), 201

@app.route('/points/type', methods=['POST'])
def add_new_type():
    new_type = request.json
    return jsonify(new_type), 201

if __name__ == '__main__':
    app.run(debug=True)
