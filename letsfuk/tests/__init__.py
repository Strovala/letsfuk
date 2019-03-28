import uuid
from random import choice, uniform

import datetime
import inject
from math import sqrt

import letsfuk
from tornado.testing import AsyncHTTPTestCase

from letsfuk.models.user import User as UserModel
from letsfuk.db import Base
from letsfuk.db.station import Station
from letsfuk.db.user import User
from letsfuk.db.session import Session
from letsfuk.ioc import testing_configuration

# Set up database for all tests
inject.clear()
inject.clear_and_configure(testing_configuration)
engine = inject.instance('db_engine')
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)


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


class UuidGenerator(Generator):
    def _generate(self):
        value = str(uuid.uuid4())
        return value


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


class GeneratorPool(object):
    def __init__(self):
        self.username = UsernameGenerator()
        self.email = EmailGenerator()
        self.latitude = LatitudeGenerator()
        self.longitude = LongitudeGenerator()
        self.uuid = UuidGenerator()


generator_pool = GeneratorPool()


class BaseAsyncHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(BaseAsyncHTTPTestCase, self).setUp()
        self.generator = generator_pool

    def get_app(self):
        return letsfuk.make_app()

    def ensure_register(self, username=None, password="Test123!", email=None):
        if username is None:
            username = self.generator.username.generate()
        if email is None:
            email = self.generator.email.generate()
        bcrypted_password = UserModel.bcrypt_password(password)
        db = inject.instance('db')
        user_id = str(uuid.uuid4())
        user = User.add(db, user_id, username, email, bcrypted_password)
        return user

    def ensure_login(self, username=None, password="Test123!", email=None):
        db = inject.instance('db')
        registered_user = self.ensure_register(
            username=username, password=password, email=email
        )
        session_id = str(uuid.uuid4())
        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(minutes=300)
        session = Session.add(
            db, session_id, registered_user.user_id, expires_at
        )
        return session, registered_user

    def add_station(self, lat=0, lon=0):
        db = inject.instance('db')
        station_id = str(uuid.uuid4())
        station = Station.add(db, station_id, lat, lon)
        return station

    def ensure_stations(self, wide=45):
        """
        Add 9 stations across -wide +wide in x and y axis
            * * *
            * * *
            * * *
        """
        stations = [
            self.add_station(-wide, wide), self.add_station(0, wide),
            self.add_station(wide, wide),
            self.add_station(-wide, 0), self.add_station(0, 0),
            self.add_station(wide, 0),
            self.add_station(-wide, -wide), self.add_station(0, -wide),
            self.add_station(wide, -wide),
        ]
        return stations

    def closest_station(self, stations, lat, lon):
        # sqrt((x1-x2)^2 +(y1-y2)^2) distance between two points
        closest_station_index = 0
        station = stations[closest_station_index]
        minimal_distance = sqrt(
            (station.latitude - lat)*(station.latitude - lat) +
            (station.longitude - lon)*(station.longitude - lon)
        )

        for i in range(1, len(stations)):
            station = stations[i]
            distance = sqrt(
                (station.latitude - lat)*(station.latitude - lat) +
                (station.longitude - lon)*(station.longitude - lon)
            )
            if distance < minimal_distance:
                minimal_distance = distance
                closest_station_index = i
        closest_station = stations[closest_station_index]
        return closest_station
