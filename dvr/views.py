from pyramid.view import view_config

from .assets import (
    convert_to_utc_seconds,
    convert_to_datetime,
    create_recording,
    delete_recording,
    TunerUnavaliable,
    TunerDoesNotExist,
    InvalidTimeRange,
    RecordingDoesNotExist,
)
from .models import (
    DBSession,
    Recording,
    Tuner,
)


@view_config(route_name='index', renderer='templates/index.pt')
def index(request):
    tuners = DBSession.query(Tuner).all()

    recordings = []
    for tuner in DBSession.query(Tuner).all():
        for recording in tuner.get_current_recordings():
            recordings.append(recording)

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
    recordings = [
        {
            "id": recording.id,
            "channel": recording.channel,
            "tuner": recording.tuner.id,
            "start_time": convert_to_utc_seconds(recording.start_time),
            "end_time": convert_to_utc_seconds(recording.end_time),
        } for recording in DBSession.query(Recording).all()
    ]
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

    try:
        new_recording = create_recording(channel, start_time, end_time, tuner_id)
    except TunerUnavaliable:
        request.response.status = 409
        return {
            "status": "failed",
            "message": "No tuner is available.",
        }
    except TunerDoesNotExist:
        request.response.status = 404
        return {
            "status": "failed",
            "message": "Tuner does not exist",
        }
    except InvalidTimeRange:
        request.response.status = 400
        return {
            "status": "failed",
            "message": "Invalid time range",
        }
    return {
        "id": new_recording.id,
        "channel": new_recording.channel,
        "tuner": new_recording.tuner_id,
        "start_time": convert_to_utc_seconds(new_recording.start_time),
        "end_time": convert_to_utc_seconds(new_recording.end_time),
    }

@view_config(
    route_name='api_delete_recordings',
    renderer='json',
    request_method="DELETE",
)
def api_delete_recordings(request):
    recording_id = request.matchdict.get("id")
    try:
        delete_recording(recording_id)
    except RecordingDoesNotExist:
        request.response.status = 404
        return {
            "status": "failed",
            "message": "Record does not exist.",
        }
    return {
        "status": "success",
        "message": "Recording deleted",
    }

def includeme(config):
    config.add_route('index', '/')
    config.add_route('api_recordings', '/api/v1/recordings')
    config.add_route('api_delete_recordings', '/api/v1/recording/{id}')
