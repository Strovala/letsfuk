import json

from letsfuk.tests import BaseAsyncHTTPTestCase


class TestUsers(BaseAsyncHTTPTestCase):
    def test_add_station(self):
        session = self.ensure_login(
            username=self.generator.username.generate(),
            email=self.generator.email.generate(),
        )
        session_id = session.session_id
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
        response_latitude = response_body.get('latitude')
        latitude = float(response_latitude)
        response_longitude = response_body.get('longitude')
        longitude = float(response_longitude)
        self.assertEqual(lat, latitude)
        self.assertEqual(lon, longitude)

    def test_subscribe(self):
        stations = self.ensure_stations()
