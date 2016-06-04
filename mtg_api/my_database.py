from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy_utils.functions import drop_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from mtg_api.config import Config, CONFIG_PATH

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

    def drop_tables(self):
        self._session.close()
        self.base.metadata.drop_all()

    def make_tables(self):
        self.base.metadata.create_all()

    def make_database(self, drop_if_exists=False):
        if drop_if_exists and database_exists(self.config.database.uri):
            self.drop_database()
            create_database(self.config.database.uri)
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
