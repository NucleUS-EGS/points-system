from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint
import json
import mysql.connector

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

    def get(self, entity_id=None):

        if entity_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM ENTITY WHERE ID = %s"
            values = (entity_id,)
            
            try:
                cursor.execute(query, values)
                result = cursor.fetchall()
                return jsonify(result)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                return Response("Failed to get entity", status=500, mimetype='application/json')
            finally:
                cursor.close()
                conn.close()

        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM ENTITY"
            
            try:
                cursor.execute(query)
                result = cursor.fetchall()
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

    # def get_history(self):
    #     # history of points of an entity
    #     # if + 10 add 10 points -> trigger that adds 10 points
    #     # if - 10 remove 10 points -> trigger that removes 10 points

    #     conn = get_db_connection()
    #     cursor = conn.cursor()
        
    #     # pessoa adiciona pontos a um id
    #     # trigger para somar e diminuir pontos

    #     query = "SELECT * FROM HISTORY"
                

# class AddSubPoints(Resource):

#     def put(self, entity_id):
#         data = request.get_json()
#         points = data.get('points')
#         if points is None:
#             return Response("{'error': 'Points value is required'}", status=400, mimetype='application/json')

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = "UPDATE ENTITY SET POINTS = POINTS + %s WHERE ID = %s;"
#         values = (points, entity_id)

#         try:
#             cursor.execute(query, values)
#             conn.commit()
#             return Response("{'message': 'Points updated successfully'}", status=200, mimetype='application/json')
#         except mysql.connector.Error as err:
#             print("Something went wrong: {}".format(err))
#             return Response("{'error': 'Failed to update points'}", status=500, mimetype='application/json')
#         finally:
#             cursor.close()
#             conn.close()


class EntityHistory(Resource):
    def get(self, entity_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM HISTORY WHERE ENTITY_ID = %s ORDER BY timestamp DESC"
        values = (entity_id,)
        
        try:
            cursor.execute(query, values)
            history = cursor.fetchall()
            if history:
                return jsonify(history)
            else:
                return jsonify({"message": "No history found for the given entity ID."})
        except mysql.connector.Error as e:
            return {"error": str(e)}, 500
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


    # podemos ter dois gets dentro de uma mesma class? 
class Standings(Resource):

    def get(self, points_type = None):
        if points_type:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM ENTITYPOINTS WHERE TIPO_ID = %s ORDER BY POINTS DESC"
            values = (points_type,)
            
            try:
                cursor.execute(query, values)
                result = cursor.fetchall()
                return jsonify(result)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                return Response("Failed to get standings", status=500, mimetype='application/json')
            finally:
                cursor.close()
                conn.close()

        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM ENTITYPOINTS ORDER BY POINTS DESC"
            
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                return Response("Failed to get standings", status=500, mimetype='application/json')
            finally:
                cursor.close()
                conn.close()



# api.add_resource(Entity, '/entity')
api.add_resource(Entity, '/entity', endpoint='all_entities')  
api.add_resource(Entity, '/entity/<entity_id>', endpoint='specific_entity')  
api.add_resource(EntityHistory, '/entity/<entity_id>/history', endpoint='entity_history')
api.add_resource(Type, '/type')
api.add_resource(Standings, '/standings', endpoint='standings')
api.add_resource(Standings, '/standings/<points_type>', endpoint='standings_type')  




# SWAGGER CONF

SWAGGER_URL = '/swagger'
API_URL = 'http://127.0.0.1:5000/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "POINTS SYSTEM"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    app.run(debug=True)



# TODO
# trigger para atualizar a tabela ENTITYPOINTS com o ID quando um novo TIPO ou ENTITY são adicionados DONE
# função que soma os pontos/tira os pontos         DONE
# PATCH /points/entity/<entity_id> - Add or remove points to an entity      NOT DONE (GET AND POST ENTITIES ARE DONE) 
# GET /points/entity/<entity_id>/history - History of points transactions   HALF DONE (NEEDS OBJECT ID)
# POST /points/type - Add a new points type        DONE
# DELETE /points/type - Remove type of points      DONE
# GET /points/standings - Get general standings of all entities  DONE
# GET /points/standings?type=<points_type> - Get standings of a points type  DONE (??)

# NOT FORGET
# object -> evento
# entity -> pessoa
# type -> nucleo