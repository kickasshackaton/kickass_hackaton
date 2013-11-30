
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Float,
    DateTime,
    ForeignKey
    )
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

Index('my_index', MyModel.name, unique=True, mysql_length=255)

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    username = Column(Text)
    password = Column(Text)
    money = Column(Float)
    mail = Column(Text)
    my_targets = relationship('Target', back_populates='user', foreign_keys='[Target.user_id]')
    overseered_targets = relationship('Target', back_populates='overseer', foreign_keys='[Target.overseer_id]')
    def __init__(self, name, username, password, money = 0, mail = "" ):
        self.name = name
        self.username = username
        self.password = password
        self.money = money
        self.mail = mail
    def __repr__(self):
        return "User id: "+str(self.id)+" name: "+ str(self.name) + " targets: " + str(len(self.my_targets)) + " overseered: " + str(len(self.overseered_targets)) +"\n"

class Target(Base):
    __tablename__ = 'Target'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    type = Column(Text)
    url = Column(Text)
    deadline = Column(DateTime)
    bid = Column(Float)
    current_progress = Column(Integer)
    planned_progress = Column(Integer)
    #source = Column(Integer, ForeignKey('User.id'))
    user_id = Column(Integer, ForeignKey('User.id'))
    overseer_id = Column(Integer, ForeignKey('User.id'))

    user = relationship('User', back_populates='my_targets', foreign_keys=[user_id])
    overseer = relationship('User', back_populates='overseered_targets', foreign_keys=[overseer_id])

    def __init__(self, name, deadline, bid, url, planned_progress = 0,current_progress = 0, type = "coursera_course"):
        self.name = name
        self.type = type
        self.deadline = deadline
        self.bid = bid
        self.current_progress = current_progress
        self.planned_progress = planned_progress
        self.url = url

