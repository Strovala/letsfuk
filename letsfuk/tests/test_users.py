import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestUsers(BaseAsyncHTTPTestCase):
    def test_register(self):
        username = self.generator.username.generate()
        email = self.generator.email.generate()
        body = {
            "username": username,
            "password": "secret",
            "email": email,
        }
        response = self.fetch(
            '/users',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(username, response_body.get('username'))
        self.assertEqual(email, response_body.get('email'))

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
        session, _ = self.ensure_login()
        session_id = session.session_id
        another_user = self.ensure_register()
        response = self.fetch(
            '/users/{}'.format(another_user.user_id),
            method="GET",
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(another_user.username, response_body.get('username'))
        self.assertEqual(another_user.email, response_body.get('email'))
        self.assertEqual(another_user.user_id, response_body.get('user_id'))

    def test_whoami(self):
        session, user = self.ensure_login()
        session_id = session.session_id
        response = self.fetch(
            '/whoami',
            method="GET",
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        response_user = response_body.get('user')
        response_session_id = response_body.get('session_id')
        self.assertEqual(user.username, response_user.get('username'))
        self.assertEqual(user.email, response_user.get('email'))
        self.assertEqual(user.user_id, response_user.get('user_id'))
        self.assertEqual(session_id, response_session_id)

    def test_get_user_not_found(self):
        session, _ = self.ensure_login()
        session_id = session.session_id
        random_uuid = self.generator.uuid.generate()
        response = self.fetch(
            '/users/{}'.format(random_uuid),
            method="GET",
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 404)

    def test_get_user_unauthorized(self):
        another_user = self.ensure_register()
        response = self.fetch(
            '/users/{}'.format(another_user.user_id),
            method="GET",
        )
        self.assertEqual(response.code, 401)
