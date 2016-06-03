from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, Column, VARCHAR
from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy_utils.functions import drop_database
from mtg_api.config import Config, CONFIG_PATH
from mtg_api import app
import os

class MyDatabase(object):

    def __init__(self, config, start=True):
        self.base = declarative_base()
        self.config = config
        self.engine = self.new_engine()
        self.session_maker = scoped_session(sessionmaker(bind=self.engine))
        if start:
            self.start()

    def new_session(self):
        if hasattr(self, "_session") and self._session:
            self._session.close()
        self._session = self.session_maker()
        return self.Session

    def start(self):
        self.new_engine()
        self.session_maker = scoped_session(sessionmaker(bind=self.engine))
        self.new_session()
        self.base.metadata.bind = self.engine
        if not database_exists(self.engine.url):
            self.make_database()
        self.base.metadata.create_all()

    def new_engine(self):
        if hasattr(self, "engine") and self.engine:
            self.engine.dispose()
        new_engine = create_engine(self.config.database.uri,
                                   pool_recycle=int(self.config.sqlalchemy.pool_recycle),
                                   pool_size=int(self.config.sqlalchemy.pool_size),
                                   echo=False)
        self.engine = new_engine
        return new_engine

    def make_database(self, drop_if_exists=False):
        if drop_if_exists and database_exists(self.config.database.uri):
            self.drop_database()
            create_database(self.config.uri)
        elif not database_exists(self.config.database.uri):
            create_database(self.config.database.uri)

    def drop_database(self):
        drop_database(self.engine.url)

    def close(self):
        self._session.close()
        self.engine.dispose()

    @property
    def Session(self):
        if not self._session.is_active:
            self._session.rollback()
            self.new_session()
        return self._session



db_instance = MyDatabase(app.custom_config)
Base = db_instance.base
def drop_db():
    cmd = "mysql -u {u} -p{p} -e 'drop database if exists {dbname}; create database {dbname};'".format(u=config.database.username,
                                                                                             p=config.database.password,
                                                                                             dbname=config.database.dbname)
    os.system(cmd)
    initialize()

id_length = 40
from uuid import uuid4
class IdMixin(object):

    def __init__(self, **kwargs):
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid4())

    @declared_attr
    def id(cls):
        return Column(VARCHAR(id_length), name='id', primary_key=True, nullable=False, default=(lambda: str(uuid4())))


class DefaultMixin():

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
