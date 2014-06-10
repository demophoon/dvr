import datetime


def get_current_time():
    return datetime.datetime.utcnow()


def convert_to_utc_seconds(date):
    beginning_of_time = datetime.datetime(1970, 1, 1)
    return int((date - beginning_of_time).total_seconds())


def convert_to_datetime(sec):
    return datetime.datetime.utcfromtimestamp(float(sec))


def get_list():
    from .models import (
        DBSession,
        Recording,
    )
    return [{
        "id": x.id,
        "start_time": x.start_time,
        "end_time": x.end_time,
        "channel": x.channel,
        "tuner": x.tuner.id,
    } for x in DBSession.query(Recording).all()]


def get_action(time):
    from .models import (
        DBSession,
        Tuner,
    )
    tuners = {}
    for tuner in DBSession.query(Tuner).all():
        tuners[tuner.id] = [x.channel for x in tuner.get_recordings(time)]
    return tuners


def delete_recording(recording_id):
    from .models import (
        DBSession,
        Recording,
    )
    record = DBSession.query(Recording).filter(Recording.id == recording_id).first()
    if not record:
        raise RecordingDoesNotExist()
    DBSession.delete(record)
    DBSession.flush()
    return True


def create_recording(channel, start_time, end_time, tuner_id=None):
    from .models import (
        DBSession,
        Tuner,
        Recording,
    )

    if start_time < get_current_time():
        start_time = get_current_time()
    if end_time < get_current_time() or end_time < start_time:
        raise InvalidTimeRange()
    # Find next available tuner
    if not tuner_id:
        tuners = DBSession.query(Tuner).all()
        next_tuner = None
        for tuner in tuners:
            if tuner.can_record(start_time, end_time):
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


class InvalidTimeRange(Exception):
    pass


class RecordingDoesNotExist(Exception):
    pass
