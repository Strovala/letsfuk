import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestUsers(BaseAsyncHTTPTestCase):
    def test_register(self):
        body = {
            "username": "random_username",
            "password": "secret",
            "email": "random_mail@gmail.com",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 201)
        response_body = json.loads(response.body.decode())
        self.assertEqual("random_username", response_body.get('username'))

    def test_register_username_not_valid(self):
        body = {
            "username": "ra",
            "password": "secret",
            "email": "random_mail@gmail.com",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_register_username_not_sent(self):
        body = {
            "password": "secret",
            "email": "random_mail@gmail.com",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_register_email_not_valid(self):
        body = {
            "username": "random_username",
            "password": "secret",
            "email": "r@g.c",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_register_email_not_sent(self):
        body = {
            "username": "random_username",
            "password": "secret",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_register_email_and_username_not_sent(self):
        body = {
            "password": "secret",
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_get_user(self):
        user = self.ensure_login(
            username=self.generator.username.generate(),
            email=self.generator.email.generate()
        )
        session_id = user.get('session_id')
        another_user = self.ensure_register(
            username=self.generator.username.generate(),
            email=self.generator.email.generate()
        )
        response = self.fetch(
            '/users/{}'.format(another_user["username"]),
            method="GET",
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(another_user["username"], response_body.get('username'))

    def test_get_user_unauthorized(self):
        another_user = self.ensure_register(
            username=self.generator.username.generate(),
            email=self.generator.email.generate()
        )
        response = self.fetch(
            '/users/{}'.format(another_user["username"]),
            method="GET",
        )
        self.assertEqual(response.code, 401)
