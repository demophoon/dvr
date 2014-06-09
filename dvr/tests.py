import unittest
import transaction

from pyramid import testing

from .models import DBSession
from .assets import (
    get_current_time,
    convert_to_utc_seconds,
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
        from .views import (
            api_get_recordings,
            api_post_recordings,
        )

        # Make sure no recordings exist
        get_request = testing.DummyRequest()
        page = api_get_recordings(get_request)
        self.assertEqual(page, [])

        # Create Recording
        start_time = convert_to_utc_seconds(get_current_time())
        end_time = start_time + 300
        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, [{
            'id': 1,
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
            'tuner': 1,
        }])

        # Ensure that two recordings cannot happen at the same time
        page = api_post_recordings(post_request)
        self.assertEqual(page, {
            "status": "failed",
            "message": "No tuner is available.",
        })

        # Ensure Recording Exists
        get_request2 = testing.DummyRequest()
        page = api_get_recordings(get_request2)
        self.assertEqual(page, [{
            'id': 1,
            'channel': 3,
            'start_time': start_time,
            'end_time': end_time,
            'tuner': 1,
        }])
