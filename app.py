from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api,  reqparse
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import json
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
api = Api(app)


load_dotenv()

# db configuration

db_config = {
    'host': os.environ.get("HOST"),
    'port': os.environ.get("PORT"),
    'user': os.environ.get("USER_NAME"),
    'password': os.environ.get("PASSWORD"),
    'database': os.environ.get('DATABASE')
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

class Entity(Resource):

    # GET /points/entity?id=entity_id - Get all entities or by type
    def get(self, entity_id=None):
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            if entity_id is not None:
                query = "SELECT * FROM ENTITY WHERE ID = %s"
                cursor.execute(query, (entity_id,))
            else:
                query = "SELECT * FROM ENTITY"
                cursor.execute(query)

            result = cursor.fetchall()
            return jsonify(result)
        except Error as err:
            return {"error": str(err)}, 500
        finally:
            cursor.close()
            conn.close()

    # POST /points/entity - Add a new entity
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

    def patch(self, entity_id):
        data = request.get_json(force=True)  
        if 'points' not in data:
            return {'message': 'Points value is required'}, 400  
        points_to_update = data['points']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "UPDATE ENTITY SET POINTS = POINTS + %s WHERE ID = %s"
        values = (points_to_update, entity_id)

        try:
            cursor.execute(query, values)
            conn.commit()
            if cursor.rowcount == 0:
                return {'message': 'Entity not found'}, 404 
            return {'message': 'Entity updated successfully'}, 200
        except mysql.connector.Error as err:
            return {'error': str(err)}, 500
        finally:
            cursor.close()
            conn.close()



    # PATCH /points/entity/<entity_id>/?object_id=<object_id> 
    # na altura de adicionar ou remover pontos -> identificar o object_id
    # se não for identificado, então os pontos são porque sim


    # se houver object id -> update table set done = TRUE
    # trigger que se em entity objetc o done = TRUE -> object id pontos soma ao entity ID
    # update history e update entity id

    # se não houver object id -> update da tabela entity com esse valor 


    # para o history
    # se adicionar pontos a uma entity só porque sim: object = null actions: old points + new points
    # se adicionar pontos e o object não for null: action: entity id old points + object id points 




class EntityObjects(Resource):

    #POST /points/entity/<entity_id>/object - Associate an object to an entity

    # by searching for that entity id, we can see what objects are associated
    # «a pessoa de id <entity_id> fez o evento de id object
    def post(self, entity_id):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO ENTITYOBJECTS (ENTITY_ID, OBJECT_ID, DONE) VALUES (%s, %s, %s)"
        values = (entity_id, data['OBJECT_ID'], data['DONE'])
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Object associated to entity", status=201, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to associate object to entity", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

    # PATCH /points/entity/<entity_id>?object_id=<object_id> - Update points of an entity
    def patch(self, entity_id):
        parser = reqparse.RequestParser()
        parser.add_argument('object', type=int, store_missing=False, location='args')
        args = parser.parse_args()
        object_id = args.get('object')
        data = request.get_json(force=True)
        entity_id = str(entity_id) 

        if 'points' not in data:
            return {'message': 'Points value is required'}, 400
        points_to_update = data['points']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            if object_id is not None:
                print("object id")
                object_query = "UPDATE ENTITYOBJECTS SET DONE = %s WHERE ENTITY_ID = %s AND OBJECT_ID = %s"
                cursor.execute(object_query, (True, entity_id, object_id,))

                action_desc = f"+{points_to_update} points" if points_to_update >= 0 else f"{points_to_update} points"
                history_query = "INSERT INTO HISTORY (ENTITY_ID, OBJECT_ID, ACTION, TIMESTAMP) VALUES (%s, %s, %s, NOW())"
                cursor.execute(history_query, (entity_id, object_id, action_desc))
            else:
                print("no object id")
                
                entity_query = "UPDATE ENTITY SET POINTS = POINTS + %s WHERE ID = %s"
                print("Executing query:", entity_query)
                print("With parameters:", (points_to_update, entity_id))
                cursor.execute(entity_query, (points_to_update, entity_id,))
                action_desc = f"+{points_to_update} points" if points_to_update >= 0 else f"{points_to_update} points"
                history_query = "INSERT INTO HISTORY (ENTITY_ID, OBJECT_ID, ACTION, TIMESTAMP) VALUES (%s, NULL, %s, NOW())"
                cursor.execute(history_query, (entity_id, action_desc))

            conn.commit()

            if cursor.rowcount > 0:
                return {'message': 'Update successful', 'rows_updated': cursor.rowcount}, 200
            else:
                return {'message': 'No rows updated'}, 404
        except Error as err:
            print("An unexpected error occurred:", str(err))
            return {"error": str(err)}, 500
        finally:
            cursor.close()
            conn.close()
    



class Type(Resource):

    # POST /points/type - Add a new points type
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

    # DELETE /points/type - Remove a points type
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

    # GET /points/standings - Get general standings of all entities
    # GET /points/standings?type=<points_type> - Get standings of a points type
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int, store_missing=False, location='args')  # Using 'points_type' for external clarity
        args = parser.parse_args()
        points_type = args.get('type')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Use dictionary=True for more accessible result handling

        try:
            if points_type is not None:
                query = "SELECT * FROM ENTITYPOINTS WHERE TIPO_ID = %s ORDER BY POINTS DESC"
                cursor.execute(query, (points_type,))
            else:
                query = "SELECT * FROM ENTITYPOINTS ORDER BY POINTS DESC"
                cursor.execute(query)

            result = cursor.fetchall()
            return jsonify(result)
        except Error as err:
            return {"error": str(err)}, 500
        finally:
            cursor.close()
            conn.close()



class Object(Resource):

    # POST /points/object - Create a new object that has a fixed amount of points associated
    def post(self):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO OBJECTS (ID, POINTS) VALUES (%s, %s)"
        values = (data['ID'], data['POINTS'])
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Object added", status=201, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to add type", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

    # PATCH /points/object/<object_id> - Retify number of points of an object
    def patch(self, object_id):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "UPDATE OBJECTS SET POINTS = %s WHERE ID = %s"
        values = (data['POINTS'], object_id)
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return Response("Object updated", status=200, mimetype='application/json')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return Response("Failed to update object", status=500, mimetype='application/json')
        finally:
            cursor.close()
            conn.close()

#class History:
# GET /points/entity/<entity_id>/history - History of points transactions   HALF DONE (NEEDS OBJECT ID)

# se em entity points a coluna done = true -> update history
# nesse update:
# object na tabela history = object na tabela entityObjects object where done = true
# entity na tabela history = entity na tabela entityObjects where done = true
# action = entityId points - or + object points
# or (se os pontos foram por um evento)
# action = entityId points - or + type points & object = null







api.add_resource(Entity, '/v1/entity', endpoint='all_entities')  
api.add_resource(Entity, '/v1/entity/<int:entity_id>', endpoint='specific_entity')  
api.add_resource(Type, '/v1/type')
api.add_resource(Standings, '/v1/standings')
api.add_resource(Object, '/v1/object')
api.add_resource(EntityObjects, '/v1/entity/<int:entity_id>/object', endpoint='associate_object')
api.add_resource(EntityObjects, '/v1/entity/<int:entity_id>', endpoint='update_points')



# SWAGGER CONF

SWAGGER_URL = '/swagger/v1'
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


# TRIGGER que se na tabela entityobjects a tabela done estiver a true então adiciona o número de pontos correspondentes a esse object ID ao entity ID
# se estiver false o número de pontos mantém-se 

# TRIGGERS
# se em ENTITY POINTS a tabela DONE estiver true, então adiciona o número de pontos correspondente a esse OBJECT ID ao ENTITY ID e atualiza o HISTORY com 
# a ACTION que foi feita (adicionou ou removeu pontos) e o esse OBJECT ID associado a essa action
    

# NOT FORGET
# object -> evento
# entity -> pessoa
# type -> nucleo
    
# ENTITY -> pontos por cada pessoa
# OBJECT -> pontos por cada evento
# TYPE -> pontos recebidos por quem?
# ENTITYPOINTS -> «recebe x pontos do NEECT»
# HISTORY -> histórico de transações de pontos
# ENTITYOBJECTS -> «recebe x pontos por ter feito y evento»
    
# HISTORY
# ENTITY_ID recebeu/ficou sem x pontos por ter feito OBJECT_ID em TIMESTAMP



# class EntityPoints(Resource):
#     def post(self, entity_id):
#         data = request.get_json()
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         query = "INSERT INTO ENTITYPOINTS (ENTITY_ID, _ID, DONE) VALUES (%s, %s, %s)"
#         values = (entity_id, data['OBJECT_ID'], data['DONE'])
        
#         try:
#             cursor.execute(query, values)
#             conn.commit()
#             return Response("Object associated to entity", status=201, mimetype='application/json')
#         except mysql.connector.Error as err:
#             print("Something went wrong: {}".format(err))
#             return Response("Failed to associate object to entity", status=500, mimetype='application/json')
#         finally:
#             cursor.close()
#             conn.close()





