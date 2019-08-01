import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestPushNotifications(BaseAsyncHTTPTestCase):
    def test_subscribe(self):
        session, user = self.ensure_login()
        endpoint = self.generator.text.generate()
        auth = self.generator.text.generate()
        p256dh = self.generator.text.generate()
        body = {
            "endpoint": endpoint,
            "keys": {
                "auth": auth,
                "p256dh": p256dh,
            }
        }
        response = self.fetch(
            '/push-notifications/subscribe',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 201)
        response_body = json.loads(response.body.decode())
        response_user_id = response_body.get('user_id')
        response_endpoint = response_body.get('endpoint')
        keys = response_body.get('keys')
        self.assertIsNotNone(keys)
        response_auth = keys.get('auth')
        response_p256dh = keys.get('p256dh')
        self.assertEqual(user.user_id, response_user_id)
        self.assertEqual(endpoint, response_endpoint)
        self.assertEqual(auth, response_auth)
        self.assertEqual(p256dh, response_p256dh)

    def test_subscribe_already_subscribed(self):
        subscriber, _, _ = self.ensure_push_sub()
        session, user = self.ensure_login()
        endpoint = subscriber.endpoint
        auth = subscriber.auth
        p256dh = subscriber.p256dh
        body = {
            "endpoint": endpoint,
            "keys": {
                "auth": auth,
                "p256dh": p256dh,
            }
        }
        response = self.fetch(
            '/push-notifications/subscribe',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 201)
        response_body = json.loads(response.body.decode())
        response_user_id = response_body.get('user_id')
        response_endpoint = response_body.get('endpoint')
        keys = response_body.get('keys')
        self.assertIsNotNone(keys)
        response_auth = keys.get('auth')
        response_p256dh = keys.get('p256dh')
        self.assertEqual(user.user_id, response_user_id)
        self.assertEqual(endpoint, response_endpoint)
        self.assertEqual(auth, response_auth)
        self.assertEqual(p256dh, response_p256dh)

    def test_unsubscribe(self):
        subscriber, session, user = self.ensure_push_sub()
        endpoint = subscriber.endpoint
        auth = subscriber.auth
        p256dh = subscriber.p256dh
        body = {
            "endpoint": endpoint,
            "keys": {
                "auth": auth,
                "p256dh": p256dh,
            }
        }
        response = self.fetch(
            '/push-notifications/unsubscribe',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 204)

    def test_check(self):
        subscriber, session, user = self.ensure_push_sub()
        endpoint = subscriber.endpoint
        auth = subscriber.auth
        p256dh = subscriber.p256dh
        response = self.fetch(
            '/push-notifications/check?endpoint={}&auth={}&p256dh={}'.format(
                endpoint, auth, p256dh
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        response_user_id = response_body.get('user_id')
        response_endpoint = response_body.get('endpoint')
        keys = response_body.get('keys')
        self.assertIsNotNone(keys)
        response_auth = keys.get('auth')
        response_p256dh = keys.get('p256dh')
        self.assertEqual(user.user_id, response_user_id)
        self.assertEqual(endpoint, response_endpoint)
        self.assertEqual(auth, response_auth)
        self.assertEqual(p256dh, response_p256dh)
