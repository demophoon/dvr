#!/usr/bin/env python
# encoding: utf-8

"""
Usage:
    dvr_admin <config_file> add <channel> <start_time> <end_time>
    dvr_admin <config_file> check <time>
    dvr_admin <config_file> list
    dvr_admin <config_file> delete <recording_id>
"""

from docopt import docopt

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import (
    DBSession,
    Base,
)

from ..assets import (
    create_recording,
    delete_recording,
)


def main():
    arguments = docopt(__doc__, version="1.0.0")

    config_file = arguments["<config_file>"]
    setup_logging(config_file)
    settings = get_appsettings(config_file)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    if arguments['add']:
        channel = arguments['<channel>']
        start_time = arguments['<start_time>']
        end_time = arguments['<end_time>']
        create_recording(channel, start_time, end_time)
    elif arguments['check']:
        time = arguments['<time>']
    elif arguments['list']:
        pass
    elif arguments['delete']:
        recording_id = arguments["recording_id"]
        delete_recording(recording_id)

    print arguments
    exit()
