import uuid
from random import choice, uniform

import datetime
import inject

import letsfuk
from tornado.testing import AsyncHTTPTestCase

from letsfuk.db.models import Base, Station, User, Session
from letsfuk.models.user import User as UserModel
from letsfuk.ioc import testing_configuration


class GeneratorPool(object):
    def __init__(self):
        self.username = UsernameGenerator()
        self.email = EmailGenerator()
        self.latitude = LatitudeGenerator()
        self.longitude = LongitudeGenerator()


class Generator(object):
    letters = [chr(ord('a') + i) for i in range(26)]
    domains = [
        "hotmail.com", "gmail.com", "aol.com",
        "mail.com", "mail.koz", "yahoo.com"
    ]

    def __init__(self):
        self.generated = set()

    def generate(self):
        slug = self._generate()
        while slug in self.generated:
            slug = self._generate()
        self.generated.add(slug)
        return slug

    def _generate(self):
        pass


class LatitudeGenerator(Generator):
    def _generate(self):
        lat = uniform(-90.0, 90.0)
        return lat


class LongitudeGenerator(Generator):
    def _generate(self):
        lon = uniform(-180.0, 180.0)
        return lon


class EmailGenerator(Generator):
    def _generate(self):
        left_side = ''.join([choice(self.letters) for _ in range(12)])
        right_side = choice(self.domains)
        email = '{}@{}'.format(left_side, right_side)
        return email


class UsernameGenerator(Generator):
    def _generate(self):
        username = ''.join([choice(self.letters) for _ in range(12)])
        return username


class BaseAsyncHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(BaseAsyncHTTPTestCase, self).setUp()
        engine = inject.instance('db_engine')
        Base.metadata.create_all(engine)
        self.generator = GeneratorPool()

    def get_app(self):
        inject.clear_and_configure(testing_configuration)
        return letsfuk.make_app()

    def tearDown(self):
        super(BaseAsyncHTTPTestCase, self).tearDown()
        engine = inject.instance('db_engine')
        db = inject.instance('db')
        try:
            db.commit()
        except Exception as _:
            db.rollback()
        Base.metadata.drop_all(bind=engine)
        inject.clear()

    def ensure_register(self, username=None, password="Test123!", email=None):
        if username is None:
            username = self.generator.username.generate()
        if email is None:
            email = self.generator.email.generate()
        bcrypted_password = UserModel.bcrypt_password(password)
        db = inject.instance('db')
        user = User.add(db, username, email, bcrypted_password)
        return user

    def ensure_login(self, username=None, password="Test123!", email=None):
        db = inject.instance('db')
        registered_user = self.ensure_register(
            username=username, password=password, email=email
        )
        session_id = str(uuid.uuid4())
        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(minutes=300)
        session = Session.add(db, session_id, registered_user.id, expires_at)
        return session

    def add_station(self, lat=0, lon=0):
        db = inject.instance('db')
        station_id = str(uuid.uuid4())
        station = Station.add(db, station_id, lat, lon)
        return station

    def ensure_stations(self):
        """
        Add 9 stations
            * * *
            * * *
            * * *
        """
        stations = [
            self.add_station(-45, 45), self.add_station(0, 45),
            self.add_station(45, 45),
            self.add_station(-45, 0), self.add_station(0, 0),
            self.add_station(45, 0),
            self.add_station(-45, -45), self.add_station(0, -45),
            self.add_station(45, -45),
        ]
        return stations
