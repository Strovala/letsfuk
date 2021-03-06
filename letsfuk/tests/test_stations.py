import json
from letsfuk.tests import BaseAsyncHTTPTestCase


class TestStations(BaseAsyncHTTPTestCase):
    def _round_value(self, value, decimal_points=6):
        value = float("{0:.{1}f}".format(value, decimal_points))
        return value

    def test_add_station(self):
        self.ensure_register(username='strovala')
        session, _ = self.ensure_login()
        session_id = session.session_id
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon
        }
        response = self.fetch(
            '/stations',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        latitude = response_body.get('lat')
        longitude = response_body.get('lon')
        self.assertEqual(self._round_value(lat), latitude)
        self.assertEqual(self._round_value(lon), longitude)
        self.assertUserWithUsername('strovala')
        station_id = response_body.get('station_id')
        self.assertMessageInStation(station_id)

    def test_add_station_invalid_lat(self):
        session, _ = self.ensure_login()
        session_id = session.session_id
        lat = 500
        lon = self.generator.longitude.generate()
        body = {
            "lat": lat,
            "lon": lon
        }
        response = self.fetch(
            '/stations',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_add_station_invalid_lon(self):
        session, _ = self.ensure_login()
        session_id = session.session_id
        lat = self.generator.latitude.generate()
        lon = 500
        body = {
            "lat": lat,
            "lon": lon
        }
        response = self.fetch(
            '/stations',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_subscribe(self):
        stations = self.ensure_stations()
        session, user = self.ensure_login(station=stations[0])
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
        station = self.closest_station(stations, lat, lon)
        self.assertEqual(station.station_id, response_body.get('station_id'))
        self.assertEqual(user.user_id, response_body.get('user_id'))

    def test_subscribe_invalid_lat_and_lon(self):
        session, user = self.ensure_login()
        session_id = session.session_id
        body = {
            "lat": "",
            "lon": "blant"
        }
        response = self.fetch(
            '/stations/subscribe',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_get_station_for_user(self):
        station = self.add_station()
        session, user = self.ensure_login(station=station)
        response = self.fetch(
            '/users/{}/station'.format(user.user_id),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        response_station_id = response_body.get('station_id')
        self.assertEqual(station.station_id, response_station_id)

    def test_get_station(self):
        station = self.add_station()
        another_station = self.add_station()
        session, _ = self.ensure_login(station=station)
        _, _ = self.ensure_login(station=station)
        _, _ = self.ensure_login(station=another_station)
        _, _ = self.ensure_login(station=station)
        response = self.fetch(
            '/stations/{}'.format(station.station_id),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        response_station = response_body.get('station')
        response_members = response_body.get('members')
        self.assertEqual(
            response_station.get('station_id'), station.station_id
        )
        self.assertEqual(len(response_members), 3)

