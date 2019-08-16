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

    def test_update_avatar(self):
        session, user = self.ensure_login()
        random_uuid = self.generator.uuid.generate()
        avatar_key = "{}/{}".format(user.username, random_uuid)
        body = {
            "avatar_key": avatar_key
        }
        response = self.fetch(
            '/users/{}'.format(user.user_id),
            method="PATCH",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(avatar_key, response_body.get('avatar_key'))

    def test_update_avatar_already_has_avatar(self):
        session, user = self.ensure_login()
        user = self.ensure_avatar(user.user_id)
        random_uuid = self.generator.uuid.generate()
        avatar_key = "{}/{}".format(user.username, random_uuid)
        body = {
            "avatar_key": avatar_key
        }
        response = self.fetch(
            '/users/{}'.format(user.user_id),
            method="PATCH",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(avatar_key, response_body.get('avatar_key'))

    def test_update_avatar_passed_int(self):
        session, user = self.ensure_login()
        body = {
            "avatar_key": 12
        }
        response = self.fetch(
            '/users/{}'.format(user.user_id),
            method="PATCH",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_update_avatar_passed_empty(self):
        session, user = self.ensure_login()
        body = {
            "avatar_key": ""
        }
        response = self.fetch(
            '/users/{}'.format(user.user_id),
            method="PATCH",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_update_avatar_no_avatar_key(self):
        session, user = self.ensure_login()
        body = {
            "blant": ""
        }
        response = self.fetch(
            '/users/{}'.format(user.user_id),
            method="PATCH",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_get_users_search_by_username(self):
        session, user_1 = self.ensure_login(username='strovala')
        _, user_2 = self.ensure_login(username='strovaletina')
        search = 'stro'
        response = self.fetch(
            '/users?username={}'.format(search),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        users = response_body.get('users')
        self.assertEqual(users[0].get('username'), user_1.username)
        self.assertEqual(users[1].get('username'), user_2.username)
