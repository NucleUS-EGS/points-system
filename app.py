from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
import mysql.connector
import json

app = Flask(__name__)
api = Api(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'EGS2324pass!',
    'database': 'POINTS'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

class Entity(Resource):

    def get(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM ENTITY"
        
        try:
            print("gatinho")
            cursor.execute(query)
            result = cursor.fetchall()
            #print(result)
            return jsonify(result)
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to get entities", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

    def post(self):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO ENTITY (ID, POINTS) VALUES (%s, %s)"
        values = (data['ID'], data['POINTS'])
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Entity added", status=201, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to add entity", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

api.add_resource(Entity, '/entity')

if __name__ == '__main__':
    app.run(debug=True)