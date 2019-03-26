import json

from letsfuk.tests import BaseAsyncHTTPTestCase, LatitudeGenerator


class TestUsers(BaseAsyncHTTPTestCase):
    def test_add_station(self):
        user = self.ensure_login(
            username=self.generator.username.generate(),
            email=self.generator.email.generate(),
        )
        session_id = user.get('session_id')
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon
        }
        response = self.fetch(
            '/stations/subscribe',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(lat, response_body.get('lat'))
        self.assertEqual(lon, response_body.get('lon'))
