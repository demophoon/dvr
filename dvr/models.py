from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Tuner(Base):
    __tablename__ = 'tuners'
    id = Column(Integer, primary_key=True)
    max_shows_to_record = Column(Integer, default=1)
    name = Column(Text)

    recordings = relationship("Recording", backref="tuner")


class Recording(Base):
    __tablename__ = 'recordings'
    id = Column(Integer, primary_key=True)
    tuner_id = Column(Integer, ForeignKey("tuners.id"))
    channel = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
