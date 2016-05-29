from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, DateTime, Float
from mtg_api import db

class Session(db.Base, db.IdMixin, db.DefaultMixin):
    __tablename__ = 'sessions'

    user_id = Column(VARCHAR(db.id_length), ForeignKey('users.id'))
    token = Column(VARCHAR(1000))
    create_date = Column(DateTime())
    expire_date = Column(DateTime())
    active = Column(Boolean(), default=True)
