import unittest
import transaction

from pyramid import testing

from .models import DBSession
from .assets import (
    get_current_time,
    convert_to_utc_seconds,
    convert_to_datetime,
)


class TestTunerSetup(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        from .models import (
            Base,
            DBSession,
            Tuner,
        )
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = Tuner(name='Base Tuner')
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import index
        from .models import (
            Tuner,
        )
        request = testing.DummyRequest()
        page = index(request)
        tuners = DBSession.query(Tuner).all()
        self.assertEqual(page['recordings'], [])
        self.assertEqual(page['tuners'], tuners)


class TestSetRecording(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        import dvr
        from sqlalchemy import create_engine
        from .models import (
            Base,
            DBSession,
            Tuner,
        )

        dvr.assets.get_current_time = lambda: convert_to_datetime(0)

        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = Tuner(name='Base Tuner')
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        import dvr
        from .views import (
            api_get_recordings,
            api_post_recordings,
        )

        # Make sure no recordings exist
        get_request = testing.DummyRequest()
        page = api_get_recordings(get_request)
        self.assertEqual(page, [])

        self.assertEqual(dvr.assets.get_current_time(), convert_to_datetime(0))

        # Create Recording
        start_time = convert_to_utc_seconds(dvr.assets.get_current_time())
        end_time = start_time + 300
        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            'id': 1,
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
            'tuner': 1,
        })

        # Ensure that two recordings cannot happen at the same time
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            "status": "failed",
            "message": "No tuner is available.",
        })

        # Ensure that we cannot push recording to a non-existent tuner
        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
            'tuner': 2,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            "status": "failed",
            "message": "Tuner does not exist",
        })

        # Ensure that Time formats are correct
        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': "12:00am",
            'end_time': "7:00pm",
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            "status": "failed",
            "message": "Invalid start time",
        })

        # Ensure that channel is an int
        post_request = testing.DummyRequest(post={
            'channel': "a",
            'start_time': start_time,
            'end_time': end_time,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            "status": "failed",
            "message": "Invalid channel",
        })

        # Ensure Recording Exists
        get_request = testing.DummyRequest()
        page = api_get_recordings(get_request)
        self.assertEqual(page, [{
            'id': 1,
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
            'tuner': 1,
        }])

        # Create Recording with start date before current time

        dvr.assets.get_current_time = lambda: convert_to_datetime(300)

        start_time = convert_to_utc_seconds(dvr.assets.get_current_time()) - 250
        end_time = 550
        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            'id': 2,
            'channel': 3,
            'start_time': 300,
            'end_time': 550,
            'tuner': 1,
        })
