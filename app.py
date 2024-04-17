from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api, reqparse
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from datetime import datetime
from db_config import * 
from models import * 
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = get_db()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = get_sqlalchemy_track_modifications()

db.init_app(app)

APIKEY = os.environ.get('APIKEY')

with app.app_context():
    engine = create_engine(get_db())
    insp = reflection.Inspector.from_engine(engine)
    if not insp.has_table(APIKEYS.__tablename__):
        print(' * Creating all tables')
        db.create_all()

        # insert APIKEY if doesn't exist
        key = APIKEYS.query.get(APIKEY)
        if not key:
            print(' * Adding API Key')
            key = APIKEYS(APIKEY)
            db.session.add(key)
            db.session.commit()


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

class APIkey(Resource):

    def get(self):
        try:
            apikeys = APIKEYS.query.all()  
            if not apikeys:  
                return jsonify([])  

            return jsonify([{'ID': apikey.ID} for apikey in apikeys])

        except Exception as e:
            return {"error": str(e)}, 500



class Entity(Resource):

    # GET /points/entity - Get all entities
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, store_missing=False, location='args') 
        args = parser.parse_args()
        id = args.get('id')

        try:
            if id is not None:
                entities = ENTITY.query.filter_by(ID=id).first()
                if entities is None:
                    return jsonify([]) 
                entities = [entities]
            else:
                entities = ENTITY.query.all()
                if entities is None:
                    return jsonify([])  

            return jsonify([{
                'ID': entity.ID,
                'POINTS': entity.POINTS,
            } for entity in entities])

        except Exception as e:
            # Handle errors that occur during database interaction
            return {"error": str(e)}, 500

    # POST /points/entity - Add a new entity
    def post(self):
        data = request.get_json()
        new_entity = ENTITY(id=data['ID'], points=data['POINTS'])
        db.session.add(new_entity)
        db.session.commit()
        return Response("Entity added", status=201, mimetype='application/json')



class EntityObjects(Resource):

    # POST /points/entity/<entity_id>/object - Associate an object to an entity
    def post(self, entity_id):
        data = request.get_json()
        
        new_entity_object = ENTITYOBJECTS(
            ENTITY_ID=entity_id,
            OBJECT_ID=data['OBJECT_ID'],
            DONE=data['DONE']
        )
        
        try:
            db.session.add(new_entity_object)
            db.session.commit()
            return Response("Object associated to entity", status=201, mimetype='application/json')
        except Exception as e:
            db.session.rollback()
            print("Something went wrong: {}".format(e))
            return Response("Failed to associate object to entity", status=500, mimetype='application/json')

    # PATCH /points/entity/<entity_id>?object_id=<object_id> - Update points of an entity
    def patch(self, entity_id):
        parser = reqparse.RequestParser()
        parser.add_argument('object', type=int, store_missing=False, location='args')
        args = parser.parse_args()
        object_id = args.get('object')
        data = request.get_json(force=True)

        if 'points' not in data:
            return {'message': 'Points value is required'}, 400
        points_to_update = data['points']

        try:
            if object_id:
                entity_object = ENTITYOBJECTS.query.filter_by(ENTITY_ID=entity_id, OBJECT_ID=object_id).first()
                if entity_object:
                    entity_object.DONE = True
                    db.session.add(entity_object)
                    
                    new_history = HISTORY(
                        ENTITY_ID=entity_id,
                        OBJECT_ID=object_id,
                        ACTION=f"+{points_to_update}" if points_to_update >= 0 else f"{points_to_update}",
                        TIMESTAMP=datetime.now()
                    )
                    db.session.add(new_history)
                else:
                    return {'message': 'Entity object not found'}, 404
            else:
                entity = ENTITY.query.filter_by(ID=entity_id).first()
                if entity:
                    entity.POINTS += points_to_update
                    db.session.add(entity)

                    new_history = HISTORY(
                        ENTITY_ID=entity_id,
                        ACTION=f"+{points_to_update}" if points_to_update >= 0 else f"{points_to_update}",
                        TIMESTAMP=datetime.now()
                    )
                    db.session.add(new_history)
                else:
                    return {'message': 'Entity not found'}, 404

            db.session.commit()
            return {'message': 'Update successful'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    



class Type(Resource):

    # POST /points/type - Add a new points type
    def post(self):
        data = request.get_json()
        new_type = TYPE(ID=data['ID'], POINTS=data['TIPO'])

        try:
            db.session.add(new_type)
            db.session.commit()
            return Response("Type added", status=201, mimetype='application/json')
        except Exception as e:
            db.session.rollback()
            print("Something went wrong: {}".format(e))
            return Response("Failed to add type", status=500, mimetype='application/json')

    # DELETE /points/type - Remove a points type
    def delete(self):
        data = request.get_json()
        tipo_id = data['ID']
        type_to_delete = TYPE.query.filter_by(ID=tipo_id).first()

        if type_to_delete is None:
            return {'message': 'Type not found'}, 404

        try:
            db.session.delete(type_to_delete)
            db.session.commit()
            return Response("Type removed", status=200, mimetype='application/json')
        except Exception as e:
            db.session.rollback()
            print("Something went wrong: {}".format(e))
            return Response("Failed to remove type", status=500, mimetype='application/json')


class Standings(Resource):

    # GET /points/standings - Get general standings of all entities
    # GET /points/standings?type=<points_type> - Get standings of a points type
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=int, store_missing=False, location='args') 
        args = parser.parse_args()
        points_type = args.get('type')

        try:
            if points_type is not None:
                # Querying standings for a specific points type
                standings = ENTITYPOINTS.query.filter_by(TIPO_ID=points_type).order_by(ENTITYPOINTS.POINTS.desc()).all()
            else:
                # Querying general standings
                standings = ENTITYPOINTS.query.order_by(ENTITYPOINTS.POINTS.desc()).all()

            return jsonify([{
                'ENTITY_ID': standing.ENTITY_ID,
                'TIPO_ID': standing.TIPO_ID,
                'POINTS': standing.POINTS
            } for standing in standings])

        except Exception as e:
            # Handle errors that occur during database interaction
            return {"error": str(e)}, 500



class Object(Resource):

    # POST /points/object - Create a new object that has a fixed amount of points associated
    def post(self):
        data = request.get_json()
        new_object = OBJECT(ID=data['ID'], POINTS=data['POINTS'])
        
        try:
            db.session.add(new_object)
            db.session.commit()
            return Response("Object added", status=201, mimetype='application/json')
        except Exception as e:
            db.session.rollback()
            print("Something went wrong: {}".format(e))
            return Response("Failed to add object", status=500, mimetype='application/json')


    # PATCH /points/object/<object_id> - Retify number of points of an object
    def patch(self, object_id):
        data = request.get_json()
        object = OBJECT.query.filter_by(ID=object_id).first()
        
        if object:
            try:
                object.POINTS = data['POINTS']
                db.session.commit()
                return Response("Object updated", status=200, mimetype='application/json')
            except Exception as e:
                db.session.rollback()
                print("Something went wrong: {}".format(e))
                return Response("Failed to update object", status=500, mimetype='application/json')
        else:
            return Response("Object not found", status=404, mimetype='application/json')

class History(Resource):

    # GET /points/entity/<entity_id>/history - History of points transactions   HALF DONE (NEEDS OBJECT ID)
    def get(self, entity_id):
        try:
            history_records = HISTORY.query.filter_by(ENTITY_ID=entity_id).all()
            
            result = [{
                'ENTITY_ID': history.ENTITY_ID,
                'OBJECT_ID': history.OBJECT_ID,
                'ACTION': history.ACTION,
                'TIMESTAMP': history.TIMESTAMP.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime for JSON
            } for history in history_records]

            return jsonify(result)
        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(Entity, '/v1/entity', endpoint='all_entities')  
api.add_resource(EntityObjects, '/v1/entity/<int:entity_id>/object', endpoint='associate_object')
api.add_resource(EntityObjects, '/v1/entity/<int:entity_id>', endpoint='update_points')
api.add_resource(Type, '/v1/type')
api.add_resource(Standings, '/v1/standings')
api.add_resource(Object, '/v1/object')
api.add_resource(History, '/v1/entity/<int:entity_id>/history')



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
    



