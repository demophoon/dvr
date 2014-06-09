import datetime


def get_current_time():
    return datetime.datetime.utcnow()


def convert_to_utc_seconds(date):
    beginning_of_time = datetime.datetime(1970, 1, 1)
    return (date - beginning_of_time).total_seconds()


def convert_to_datetime(sec):
    return datetime.datetime.utcfromtimestamp(float(sec))


def create_recording(channel, start_time, end_time, tuner_id=None):
    from .models import (
        DBSession,
        Tuner,
        Recording,
    )

    # Find next available tuner
    if not tuner_id:
        tuners = DBSession.query(Tuner).all()
        next_tuner = None
        for tuner in tuners:
            if tuner.can_record(start_time):
                next_tuner = tuner
                break
        if not next_tuner:
            raise TunerUnavaliable()
        tuner = next_tuner
    else:
        tuner = DBSession.query(Tuner).filter(
            Tuner.id == tuner_id,
        ).first()
        if not tuner:
            raise TunerDoesNotExist()
    tuner_id = tuner.id

    new_recording = Recording(
        channel=channel,
        tuner_id=tuner_id,
        start_time=start_time,
        end_time=end_time,
    )
    DBSession.add(new_recording)
    DBSession.flush()
    return new_recording


# Custom Exceptions


class TunerUnavaliable(Exception):
    pass


class TunerDoesNotExist(Exception):
    pass
