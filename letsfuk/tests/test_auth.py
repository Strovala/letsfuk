import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestAuth(BaseAsyncHTTPTestCase):
    def test_login_with_username_provided_valid_email(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "username": registered_user.username,
            "email": registered_user.email,
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
        email = user.get('email')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_with_username_provided_wrong_email(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "username": registered_user.username,
            "email": registered_user.username,
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
        email = user.get('email')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_with_username(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "username": registered_user.username,
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
        email = user.get('email')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_with_email_provided_valid_username(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "email": registered_user.email,
            "username": registered_user.username,
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
        username = user.get('username')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_with_email_provided_wrong_username(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "email": registered_user.email,
            "username": registered_user.email,
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
        username = user.get('username')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_with_email(self):
        _ = self.add_station()
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "email": registered_user.email,
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
        username = user.get('username')
        user_id = user.get('user_id')
        self.assertEqual(registered_user.username, username)
        self.assertEqual(registered_user.email, email)
        self.assertEqual(registered_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(response_body.get('station_id'))

    def test_login_already_loggedin(self):
        station = self.ensure_one_station()
        password = "Test123!"
        session, loggedin_user = self.ensure_login(
            password=password, station=station
        )
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon,
            "username": loggedin_user.username,
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
        email = user.get('email')
        user_id = user.get('user_id')
        self.assertEqual(loggedin_user.username, username)
        self.assertEqual(loggedin_user.email, email)
        self.assertEqual(loggedin_user.user_id, user_id)
        session_id = response_body.get('session_id')
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(station.station_id, response_body.get('station_id'))

    def test_login_invalid_lat_and_lon(self):
        password = "Test123!"
        registered_user = self.ensure_register(password=password)
        body = {
            "lat": "",
            "lon": "blant",
            "username": registered_user.username,
            "password": password
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_login_not_registered(self):
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
            "username": registered_user.username,
            "password": "nas je kole jeb'o toroman"
        }
        response = self.fetch(
            '/auth/login',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 400)

    def test_logout(self):
        session, _ = self.ensure_login()
        response = self.fetch(
            '/auth/logout',
            method="POST",
            body=json.dumps(dict()).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        message = response_body.get('message')
        self.assertIn("logged out", message)

    def test_logout_unauthorized(self):
        response = self.fetch(
            '/auth/logout',
            method="POST",
            body=json.dumps(dict()).encode('utf-8')
        )
        self.assertEqual(response.code, 401)

    def test_logout_session_expired(self):
        import inject
        import time
        from letsfuk import Config
        session_ttl_seconds = 2
        config = inject.instance(Config)
        config.set('session_ttl', session_ttl_seconds)
        session, _ = self.ensure_login()
        time.sleep(session_ttl_seconds + 1)
        response = self.fetch(
            '/auth/logout',
            method="POST",
            body=json.dumps(dict()).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 401)
        response_body = json.loads(response.body.decode())
        text = response_body.get('text')
        self.assertAlmostEqual("Your session is expired", text)
