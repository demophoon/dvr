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

    def test_tuner_setup(self):
        from .views import index
        from .models import (
            Tuner,
        )
        request = testing.DummyRequest()
        page = index(request)
        tuners = DBSession.query(Tuner).all()
        self.assertEqual(page['recordings'], [])
        self.assertEqual(page['tuners'], tuners)
