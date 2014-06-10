from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    and_,
    or_,
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

from .assets import get_current_time


class Tuner(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

    __tablename__ = 'tuners'
    id = Column(Integer, primary_key=True)
    max_shows_to_record = Column(Integer, default=1)
    name = Column(Text)

    recordings = relationship("Recording", backref="tuner")

    def get_current_recordings(self):
        return self.get_recordings(get_current_time())

    def get_recordings(self, record_time):
        recordings = DBSession.query(Recording).join(Tuner).filter(
            self.id == Recording.tuner_id,
        ).filter(
            and_(
                record_time >= Recording.start_time,
                record_time < Recording.end_time,
            )
        ).all()
        return recordings

    def get_recordings_between(self, start_time, end_time):

        recordings = DBSession.query(Recording).join(Tuner).filter(
            self.id == Recording.tuner_id,
        ).filter(
            or_(
                # Segment is on start_time border
                and_(
                    Recording.end_time >= start_time,
                    Recording.end_time <= end_time,
                    Recording.start_time <= start_time,
                    Recording.start_time < end_time,
                ),
                # Segment is on end_time border
                and_(
                    Recording.end_time >= start_time,
                    Recording.end_time >= end_time,
                    Recording.start_time <= end_time,
                    Recording.start_time >= start_time,
                ),
                # Between start_time and end_time
                and_(
                    Recording.start_time >= start_time,
                    Recording.end_time >= start_time,
                    Recording.start_time <= end_time,
                    Recording.end_time <= end_time,
                ),
                # Segment is greater than queried period
                and_(
                    Recording.start_time <= start_time,
                    Recording.start_time <= end_time,
                    Recording.end_time >= start_time,
                    Recording.end_time >= end_time,
                ),
            )
        ).all()
        return recordings

    def can_record(self, start_time, end_time):
        return len(
            self.get_recordings_between(start_time, end_time)
        ) < self.max_shows_to_record


class Recording(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

    __tablename__ = 'recordings'
    id = Column(Integer, primary_key=True)
    tuner_id = Column(Integer, ForeignKey("tuners.id"))
    channel = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
