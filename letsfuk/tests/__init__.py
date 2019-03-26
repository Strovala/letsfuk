from random import choice, uniform

import inject
import json

import letsfuk
from tornado.testing import AsyncHTTPTestCase

from letsfuk.db.models import Base
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

    def ensure_register(
            self, username="random_username",
            password="Test123!", email="random_mail@gmail.com"
    ):
        body = {
            "username": username,
            "password": password,
            "email": email,
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 201)
        response_body = json.loads(response.body.decode())
        return response_body

    def ensure_login(
            self, username="random_username",
            password="Test123!", email="random_mail@gmail.com"
    ):
        registered_user = self.ensure_register(
            username=username, password=password, email=email
        )
        body = {
            "username": registered_user["username"],
            "password": password,
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        return response_body
