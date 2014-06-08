import datetime


def get_current_time():
    return datetime.datetime.utcnow()


def convert_to_utc_seconds(date):
    beginning_of_time = datetime.datetime(1970, 1, 1)
    return (date - beginning_of_time).total_seconds()


def convert_to_datetime(sec):
    return datetime.datetime.utcfromtimestamp(float(sec))
