from pyramid.view import view_config

from .assets import (
    convert_to_utc_seconds,
    convert_to_datetime,
)
from .models import (
    DBSession,
    Recording,
    Tuner,
)


@view_config(route_name='index', renderer='templates/index.pt')
def index(request):
    recordings = DBSession.query(Recording).all()
    tuners = DBSession.query(Tuner).all()
    return {
        'recordings': recordings,
        'tuners': tuners,
    }


@view_config(
    route_name='api_recordings',
    renderer='json',
    request_method="GET",
)
def api_get_recordings(request):
    recordings = []
    for tuner in DBSession.query(Tuner).all():
        for recording in tuner.get_current_recordings():
            recordings.append({
                "id": recording.id,
                "channel": recording.channel,
                "tuner": recording.tuner.id,
                "start_time": convert_to_utc_seconds(recording.start_time),
                "end_time": convert_to_utc_seconds(recording.end_time),
            })
    return recordings


@view_config(
    route_name='api_recordings',
    renderer='json',
    request_method="POST",
)
def api_post_recordings(request):
    channel = request.POST.get("channel")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    tuner_id = request.POST.get("tuner")
    if isinstance(channel, str):
        if not channel.isdigit():
            request.response.status = 400
            return {
                "status": "failed",
                "message": "Invalid channel",
            }
        else:
            channel = int(channel)
    if isinstance(start_time, str):
        if not start_time.isdigit():
            request.response.status = 400
            return {
                "status": "failed",
                "message": "Invalid start time",
            }
        else:
            start_time = int(start_time)
    if isinstance(end_time, str):
        if not end_time.isdigit():
            request.response.status = 400
            return {
                "status": "failed",
                "message": "Invalid end time",
            }
        else:
            end_time = int(end_time)
    start_time = convert_to_datetime(start_time)
    end_time = convert_to_datetime(end_time)
    if not tuner_id:
        tuners = DBSession.query(Tuner).all()
        next_tuner = None
        for tuner in tuners:
            if tuner.can_record(start_time):
                next_tuner = tuner
                break
        if not next_tuner:
            request.response.status = 409
            return {
                "status": "failed",
                "message": "No tuner is available.",
            }
        tuner = next_tuner
    else:
        tuner = DBSession.query(Tuner).filter(
            Tuner.id == tuner_id,
        ).first()
        if not tuner:
            return {
                "status": "failed",
                "message": "Tuner does not exist",
            }
    new_recording = Recording(
        channel=channel,
        tuner_id=tuner.id,
        start_time=start_time,
        end_time=end_time,
    )
    DBSession.add(new_recording)
    DBSession.flush()
    return [{
        "id": new_recording.id,
        "channel": new_recording.channel,
        "tuner": new_recording.tuner_id,
        "start_time": convert_to_utc_seconds(new_recording.start_time),
        "end_time": convert_to_utc_seconds(new_recording.end_time),
    }]


def includeme(config):
    config.add_route('index', '/')
    config.add_route('api_recordings', '/api/v1/recordings')
