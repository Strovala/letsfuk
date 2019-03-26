import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestAuth(BaseAsyncHTTPTestCase):
    def test_login_with_username(self):
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        body = {
            "username": registered_user["username"],
            "password": password
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        user = response_body.get('user', dict())
        username = user.get('username')
        self.assertEqual(registered_user["username"], username)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)

    def test_login_with_email(self):
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        body = {
            "email": registered_user["email"],
            "password": password
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        user = response_body.get('user', dict())
        email = user.get('email')
        self.assertEqual(registered_user["email"], email)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)

    def test_login_not_registred(self):
        body = {
            "username": "random_username",
            "password": "secret"
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_login_wrong_username(self):
        password = "Test123!"
        _ = self.ensure_register(password=password)
        body = {
            "username": "nas je kole jeb'o toroman",
            "password": password
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_login_wrong_email(self):
        password = "Test123!"
        _ = self.ensure_register(password=password)
        body = {
            "email": "nas je kole jeb'o toroman",
            "password": password
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_login_wrong_password(self):
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        body = {
            "username": registered_user["username"],
            "password": "nas je kole jeb'o toroman"
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)
