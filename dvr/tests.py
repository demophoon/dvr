import unittest
import transaction

from pyramid import testing

from .models import DBSession


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
        from .models import (
            Recording,
        )
        get_request = testing.DummyRequest()
        page = api_get_recordings(get_request)
        self.assertEqual(page, [])

        post_request = testing.DummyRequest(post={
            'channel': 3,
            'start_time': 0,
            'end_time': 0,
        })
        page = api_post_recordings(post_request)
        self.assertEqual(page, [{
            'channel': 3,
            'start_time': 0,
            'end_time': 0,
            'tuner': 1,
        }])
