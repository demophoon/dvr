from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    and_,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

from .assets import get_current_time


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Tuner(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

    __tablename__ = 'tuners'
    id = Column(Integer, primary_key=True)
    max_shows_to_record = Column(Integer, default=1)
    name = Column(Text)

    recordings = relationship("Recording", backref="tuner")

    @classmethod
    def get_current_recordings(klass):
        return klass.get_recordings(get_current_time())

    @classmethod
    def get_recordings(klass, record_time):
        recordings = DBSession.query(Recording).filter(
            and_(
                record_time >= Recording.start_time,
                record_time < Recording.end_time,
            )
        ).all()
        return recordings

    @classmethod
    def can_record(klass, record_time):
        return len(
            klass.get_recordings(record_time)
        ) < klass.max_shows_to_record


class Recording(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

    __tablename__ = 'recordings'
    id = Column(Integer, primary_key=True)
    tuner_id = Column(Integer, ForeignKey("tuners.id"))
    channel = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
