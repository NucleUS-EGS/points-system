from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from db_config import db

# create table ENTITY
class ENTITY(db.Model):

    __tablename__ = 'ENTITY'
    ID = db.Column(db.String(100), primary_key=True)
    POINTS = db.Column(db.Integer)

    def __init__(self, id, points):
        self.ID = id
        self.POINTS = points

    def to_dict(self):
        return {
            "ID": self.ID,
            "POINTS": self.POINTS
        }

# create table TYPE
class TYPE(db.Model):

    __tablename__ = 'TYPE'
    ID = db.Column(db.String(100), primary_key=True)
    POINTS = db.Column(db.Integer)

    def __init__(self, id, points):
        self.ID = id
        self.POINTS = points

    def to_dict(self):
        return {
            "ID": self.ID,
            "POINTS": self.POINTS
    }

    def __repr__(self):
        return '<Type %r has points %r>' % self.ID, self.POINTS
    
# create table OBJECTS
class OBJECT(db.Model):

    __tablename__ = 'OBJECT'
    ID = db.Column(db.String(100), primary_key=True)
    POINTS = db.Column(db.Integer)

    def __init__(self, id, points):
        self.ID = id
        self.POINTS = points

    def to_dict(self):
        return {
            "ID": self.ID,
            "POINTS": self.POINTS
    }
    
    def __repr__(self):
        return '<Type %r has points %r>' % self.ID, self.POINTS
    
class ENTITYOBJECTS(db.Model):

    __tablename__ = 'ENTITYOBJECTS'
    ENTITY_ID = db.Column(db.String(100), db.ForeignKey('ENTITY.ID'), primary_key=True)
    OBJECT_ID = db.Column(db.String(100), db.ForeignKey('OBJECT.ID'), primary_key=True)
    DONE = db.Column(db.Boolean, default=False)

    def __init__(self, entity_id, object_id, done):
        self.ENTITY_ID = entity_id,
        self.OBJECT_ID = object_id,
        self.DONE = done

    def to_dict(self):
        return {
            "ENTITY_ID": self.ENTITY_ID,
            "OBJECT_ID": self.OBJECT_ID,
            "DONE": self.DONE
    }

    def __repr__(self):
        return '<User %r>' % self.username
    
class ENTITYPOINTS(db.Model):

    __tablename__ = 'ENTITYPOINTS'
    ENTITY_ID = db.Column(db.String(100), db.ForeignKey('ENTITY.ID'), primary_key=True)
    TYPE_ID = db.Column(db.String(100), db.ForeignKey('TYPE.ID'), primary_key=True)
    POINTS = db.Column(db.Integer)
        
    def __init__(self, entity_id, type_id, points):
        self.ENTITY_ID = entity_id,
        self.TYPE_ID = type_id,
        self.POINTS = points

    
    def to_dict(self):
        return {
            "ENTITY_ID": self.entity_id,
            "TYPE_ID": self.type_id,
            "POINTS": self.points
    }

    def __repr__(self):
        return '<User %r>' % self.username
    
class HISTORY(db.Model):

    __tablename__ = 'HISTORY'
    ENTITY_ID = db.Column(db.String(100), db.ForeignKey('ENTITY.ID'),  primary_key=True)
    ACTION = db.Column(db.Integer)
    OBJECT_ID = db.Column(db.String(100), db.ForeignKey('OBJECT.ID'),  primary_key=True)
    TIMESTAMP = db.Column (db.DateTime, nullable=False, default=datetime)

    def __init__(self, entity_id, action, object_id, timestamp):
        self.ENTITY_ID = entity_id, 
        self.ACTION = action,
        self.OBJECT_ID = object_id,
        self.TIMESTAMP = timestamp

    def to_dict(self):
        return {
            "ENTITY_ID": self.entity_id,
            "ACTION": self.action,
            "OBJECT_ID": self.object_id,
            "TIMESTAMP": self.timestamp
    }

    def __repr__(self):
        return '<User %r>' % self.username