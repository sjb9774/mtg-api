from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, Column, VARCHAR
from mtg_api.config import config
import os

def new_engine(uri=None):
    if not uri:
        uri = config.database.uri
    return create_engine(uri, pool_recycle=3600, pool_size=100)
engine = new_engine()
my_session_maker = scoped_session(sessionmaker(bind=engine))

Session = my_session_maker()
Base = declarative_base()

# python 2.x does not support a single kwarg after variable-length positional args :\
# manually parse drop_all_kwarg for 'drop_all' flag
def drop_tables(*tables, **drop_all_kwarg):
    from _mysql_exceptions import IntegrityError
    global engine
    from mtg_api.models import magic
    drop_all = drop_all_kwarg.get('drop_all', False)
    go_again = True
    all_attrs = [attr for attr in dir(magic) if hasattr(getattr(magic, attr), '__table__')]
    while go_again:
        go_again = False
        for attr_name in all_attrs:
            attr = getattr(magic, attr_name)
            if attr.__tablename__ in tables or drop_all:
                try:
                    attr.__table__.drop(engine, checkfirst=True)
                # foreign key constraint, we'll get it next time ;)
                except:
                    go_again = True

def drop_db():
    cmd = "mysql -u {u} -p{p} -e 'drop database if exists {dbname}; create database {dbname};'".format(u=config.database.username,
                                                                                             p=config.database.password,
                                                                                             dbname=config.database.dbname)
    os.system(cmd)
    initialize()


def initialize():
    global Session
    global Base
    global my_session_maker
    global engine
    engine.dispose()
    engine = new_engine()
    my_session_maker = scoped_session(sessionmaker(bind=engine))
    Session = my_session_maker()
    Base.metadata.bind = engine

    Base.metadata.create_all()

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
        Session.add(self)
        if commit:
            Session.commit()
        return self

    def delete(self, commit=True):
        Session.delete(self)
        if commit:
            Session.commit()
        return self

    def update(self, **kwargs):
        commit = kwargs.pop('commit', False)
        for attr, val in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, val)
        if commit:
            Session.commit()
        return self

    @classmethod
    def get(self, uuid):
        return Session.query(self).get(uuid)

    @classmethod
    def join(self, other, column=None):
        if column:
            return Session.query(self).join(other, column)
        else:
            return Session.query(self).join(other)

    @classmethod
    def all(self):
        return Session.query(self).filter(self.id != None).all()

    @classmethod
    def filter(self, *args, **kwargs):
        return Session.query(self).filter(*args, **kwargs)

    @classmethod
    def filter_by(self, **kwargs):
        return Session.query(self).filter_by(**kwargs)

    @classmethod
    def get_or_make(self, **filter_by_kwargs):
        existing = Session.query(self).filter_by(**filter_by_kwargs).first()
        if existing:
            return existing
        else:
            new_instance = self()
            for arg, val in filter_by_kwargs.iteritems():
                if hasattr(new_instance, arg):
                    setattr(new_instance, arg, val)
            return new_instance.insert(commit=False)
