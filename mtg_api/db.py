from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, VARCHAR
from mtg_api.my_database import MyDatabase
import os

def drop_db():
    cmd = "mysql -u {u} -p{p} -e 'drop database if exists {dbname}; create database {dbname};'".format(u=config.database.username,
                                                                                                       p=config.database.password,
                                                                                                       dbname=config.database.dbname)
    os.system(cmd)
    initialize()

db_instance = None
Base = None

def setup_database(db):
    global db_instance
    global Base
    db_instance = db
    Base = db_instance.base

id_length = 40
from uuid import uuid4
class IdMixin(object):

    def __init__(self, **kwargs):
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid4())

    @declared_attr
    def id(cls):
        return Column(VARCHAR(id_length), name='id', primary_key=True, nullable=False, default=(lambda: str(uuid4())))


class DefaultMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()+'s'

    def insert(self, commit=True):
        db_instance.Session.add(self)
        if commit:
            db_instance.Session.commit()
        return self

    def delete(self, commit=True):
        db_instance.Session.delete(self)
        if commit:
            db_instance.Session.commit()
        return self

    def update(self, **kwargs):
        commit = kwargs.pop('commit', False)
        for attr, val in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, val)
        if commit:
            db_instance.Session.commit()
        return self

    @classmethod
    def get(self, uuid):
        return db_instance.Session.query(self).get(uuid)

    @classmethod
    def join(self, other, column=None):
        if column:
            return db_instance.Session.query(self).join(other, column)
        else:
            return db_instance.Session.query(self).join(other)

    @classmethod
    def all(self):
        return db_instance.Session.query(self).filter(self.id != None).all()

    @classmethod
    def filter(self, *args, **kwargs):
        return db_instance.Session.query(self).filter(*args, **kwargs)

    @classmethod
    def filter_by(self, **kwargs):
        return db_instance.Session.query(self).filter_by(**kwargs)

    @classmethod
    def get_or_make(self, **filter_by_kwargs):
        existing = db_instance.Session.query(self).filter_by(**filter_by_kwargs).first()
        if existing:
            return existing
        else:
            new_instance = self()
            for arg, val in filter_by_kwargs.iteritems():
                if hasattr(new_instance, arg):
                    setattr(new_instance, arg, val)
            return new_instance.insert(commit=False)
