from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
import mysql.connector
import json

app = Flask(__name__)
api = Api(app)

# db configuration
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

    # GET /points/entity - Get all entities
    # POST /points/entity - Add a new entity

    def get(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM ENTITY"
        
        try:
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


class Type(Resource):

    # POST /points/type - Add a new points type
    # DELETE /points/type - Remove type of points

    def post(self):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # este id representa um novo tipo
        query = "INSERT INTO TIPOS (ID, TIPO) VALUES (%s, %s)"
        values = (data['ID'], data['TIPO'])
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Type added", status=201, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to add type", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

    def delete(self):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM TIPOS WHERE ID = %s"
        values = (data['ID'],)
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Type removed", status=200, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to remove type", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

class Standings(Resource):

    #GET /points/standings - Get general standings of all entities
    #GET /points/standings?type=<points_type> - Get standings of a points type

    def get(self):
        # get 
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM ENTITY"
        
        try:
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








api.add_resource(Entity, '/entity')
api.add_resource(Type, '/type')

if __name__ == '__main__':
    app.run(debug=True)