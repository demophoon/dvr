#!/usr/bin/env python
# encoding: utf-8

"""
Usage:
    dvr_admin <config_file> add <channel> <start_time> <end_time>
    dvr_admin <config_file> check <time>
    dvr_admin <config_file> list
    dvr_admin <config_file> delete <recording_id>
    dvr_admin <config_file> add tuner
    dvr_admin <config_file> list tuner
    dvr_admin <config_file> delete tuner <tuner_id>
"""

import time
import datetime
import pprint

from docopt import docopt

import transaction
import parsedatetime

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import (
    DBSession,
    Base,
    Tuner,
)

from ..assets import (
    convert_to_datetime,
    create_recording,
    delete_recording,
    get_action,
    get_list,
)


def main():

    arguments = docopt(__doc__, version="1.0.0")

    config_file = arguments["<config_file>"]
    setup_logging(config_file)
    settings = get_appsettings(config_file)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    parser = parsedatetime.Calendar()

    if arguments['add']:
        if arguments['tuner']:
            DBSession.add(Tuner())
            print "Successfully added tuner"
        else:
            channel = arguments['<channel>']
            start_time = datetime.datetime.fromtimestamp(
                time.mktime(parser.parse(arguments['<start_time>'])[0])
            )
            end_time = datetime.datetime.fromtimestamp(
                time.mktime(parser.parse(arguments['<end_time>'])[0])
            )

            pprint.pprint(create_recording(channel, start_time, end_time))
    elif arguments['check']:
        start_time = datetime.datetime.fromtimestamp(
            time.mktime(parser.parse(arguments['<time>'])[0])
        )
        tuners = get_action(start_time)
        for tuner in tuners:
            if tuners[tuner]:
                print "Tuner %d: %s" % (tuner, ', '.join([
                    "Recording channel %d" % x for x in tuners[tuner]
                ]))
            else:
                print "Tuner %d: Not Recording" % tuner
    elif arguments['list']:
        if arguments['tuner']:
            tuners = ["Tuner %d" % x.id for x in DBSession.query(Tuner).all()]
            pprint.pprint(tuners)
        else:
            pprint.pprint(get_list())
    elif arguments['delete']:
        if arguments['tuner']:
            tuner = DBSession.query(Tuner).filter(
                Tuner.id == int(arguments["<tuner_id>"])
            ).first()
            DBSession.delete(tuner)
            print "Successfully deleted tuner"
        else:
            recording_id = arguments["<recording_id>"]
            pprint.pprint(delete_recording(recording_id))

    transaction.commit()

    exit()
