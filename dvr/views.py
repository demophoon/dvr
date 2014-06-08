import datetime

from pyramid.view import view_config

from sqlalchemy import (
    and_,
)

from .models import (
    DBSession,
    Recording,
    Tuner,
)


def get_current_time():
    return datetime.datetime.utcnow()


def get_current_recordings():
    return get_recordings(get_current_time())


def get_recordings(recording_time):
    recordings = DBSession.query(Recording).filter(
        and_(
            recording_time >= Recording.start_time,
            recording_time < Recording.end_time,
        )
    ).all()
    return recordings


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
    return [{
        "channel": x.channel,
        "tuner": x.tuner.id,
        "start_time": x.start_time.strftime("%s"),
        "end_time": x.end_time.strftime("%s"),
    } for x in get_current_recordings()]


@view_config(
    route_name='api_recordings',
    renderer='json',
    request_method="POST",
)
def api_post_recordings(request):
    channel = request.POST.get("channel")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    tuner = request.POST.get("tuner")
    return [{
        "channel": channel,
        "tuner": 1,
        "start_time": start_time,
        "end_time": end_time,
    }]


def includeme(config):
    config.add_route('index', '/')
    config.add_route('api_recordings', '/api/v1/recordings')
