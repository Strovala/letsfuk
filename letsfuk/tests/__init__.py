import uuid
from random import choice, uniform

import inject
from math import sqrt
from datetime import datetime, timedelta

import letsfuk
from tornado.testing import AsyncHTTPTestCase

from letsfuk import Config
from letsfuk.models.user import User as UserModel
from letsfuk.db import Base, commit
from letsfuk.db.models import Station, Subscriber, PrivateChat, StationChat
from letsfuk.db.models import User
from letsfuk.db.models import Session
from letsfuk.db.models import Unread
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


class TextGenerator(Generator):
    letters = (
        [chr(ord('a') + i) for i in range(26)] +
        list(' !@#$%^&*./,>?|\'\\/')
    )

    def _generate(self):
        text = ''.join([choice(self.letters) for _ in range(100)])
        return text


class GeneratorPool(object):
    def __init__(self):
        self.username = UsernameGenerator()
        self.email = EmailGenerator()
        self.latitude = LatitudeGenerator()
        self.longitude = LongitudeGenerator()
        self.uuid = UuidGenerator()
        self.text = TextGenerator()


generator_pool = GeneratorPool()


class BaseAsyncHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(BaseAsyncHTTPTestCase, self).setUp()
        self.generator = generator_pool

    def get_app(self):
        return letsfuk.make_app()

    def ensure_register(
            self, username=None, password="Test123!", email=None, station=None
    ):
        if username is None:
            username = self.generator.username.generate()
        if email is None:
            email = self.generator.email.generate()
        bcrypted_password = UserModel.bcrypt_password(password)
        db = inject.instance('db')
        user_id = str(uuid.uuid4())
        user = User.add(db, user_id, username, email, bcrypted_password)
        if station is not None:
            _ = self.subscribe(station.station_id, user.user_id)
        return user

    def ensure_login(
            self, username=None, password="Test123!", email=None, station=None
    ):
        db = inject.instance('db')
        config = inject.instance(Config)
        registered_user = self.ensure_register(
            username=username, password=password, email=email
        )
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session_ttl = config.get('session_ttl', 946100000)
        expires_at = now + timedelta(seconds=session_ttl)
        session = Session.add(
            db, session_id, registered_user.user_id, expires_at
        )
        if station is None:
            station = self.add_station()
        _ = self.subscribe(station.station_id, registered_user.user_id)
        return session, registered_user

    def add_station(self, lat=None, lon=None):
        if lat is None:
            lat = self.generator.latitude.generate()
        if lon is None:
            lon = self.generator.longitude.generate()
        db = inject.instance('db')
        station_id = str(uuid.uuid4())
        station = Station.add(db, station_id, lat, lon)
        return station

    def ensure_one_station(self):
        db = inject.instance('db')
        all_stations = db.query(Station).all()
        if len(all_stations) > 0:
            return all_stations[0]
        station = self.add_station()
        return station

    def ensure_stations(self, wide=45):
        """
        Add 9 stations across -wide +wide in x and y axis
            * * *
            * * *
            * * *
        """
        # Drop database to ensure these are only stations
        db = inject.instance('db')
        sbs = db.query(Subscriber).all()
        ss = db.query(Station).all()
        scs = db.query(StationChat).all()
        unreads = db.query(Unread).all()
        for unread in unreads:
            db.delete(unread)
            commit(db)
        for sc in scs:
            db.delete(sc)
            commit(db)
        for sb in sbs:
            db.delete(sb)
            commit(db)
        for s in ss:
            db.delete(s)
            commit(db)

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
            (station.latitude - lat) * (station.latitude - lat) +
            (station.longitude - lon) * (station.longitude - lon)
        )

        for i in range(1, len(stations)):
            station = stations[i]
            distance = sqrt(
                (station.latitude - lat) * (station.latitude - lat) +
                (station.longitude - lon) * (station.longitude - lon)
            )
            if distance < minimal_distance:
                minimal_distance = distance
                closest_station_index = i
        closest_station = stations[closest_station_index]
        return closest_station

    def subscribe(self, station_id, user_id):
        db = inject.instance('db')
        subscriber = Subscriber.add(db, station_id, user_id)
        return subscriber

    def add_private_message(self, sender_id, receiver_id):
        db = inject.instance('db')
        message_id = self.generator.uuid.generate()
        text = self.generator.text.generate()
        now = datetime.utcnow()
        sender_id = str(sender_id)
        receiver_id = str(receiver_id)
        message = PrivateChat.add(
            db, message_id, receiver_id, sender_id, text, now
        )
        return message

    def add_group_message(self, sender_id, receiver_id):
        db = inject.instance('db')
        message_id = self.generator.uuid.generate()
        text = self.generator.text.generate()
        now = datetime.utcnow()
        sender_id = str(sender_id)
        receiver_id = str(receiver_id)
        message = StationChat.add(
            db, message_id, receiver_id, sender_id, text, now
        )
        return message

    def make_station_chat(self, station, users=None):
        if users is None:
            users = [self.ensure_register() for _ in range(5)]
            _ = [
                self.subscribe(station.station_id, user.user_id)
                for user in users
            ]
        messages = [
            self.add_group_message(user.user_id, station.station_id)
            for _ in range(4)
            for user in users
        ]
        return messages

    def make_private_chat(self, user, another_user):
        messages = [
            self.add_private_message(user_a.user_id, user_b.user_id)
            for _ in range(10)
            for user_a, user_b in [(user, another_user), (another_user, user)]
        ]
        return messages

    def make_chats(self):
        station = self.add_station()
        session, user = self.ensure_login(station=station)
        another_user = self.ensure_register(station=station)
        third_user = self.ensure_register(station=station)
        station_chat = self.make_station_chat(
            station, [user, another_user, third_user]
        )
        second_chat = self.make_private_chat(user, another_user)
        # first because messages are sent later
        first_chat = self.make_private_chat(third_user, user)
        _ = self.make_private_chat(third_user, another_user)
        private_chats = [
            {
                "receiver_id": third_user.user_id,
                "messages": first_chat
            },
            {
                "receiver_id": another_user.user_id,
                "messages": second_chat
            }
        ]
        return session, station_chat, private_chats

    def ensure_unreads(self, receiver_id, station_id=None, sender_id=None):
        db = inject.instance('db')
        unread = Unread.add(
            db, receiver_id, station_id=station_id, sender_id=sender_id
        )
        return unread
