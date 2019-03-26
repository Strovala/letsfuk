import json

from letsfuk.tests import BaseAsyncHTTPTestCase


class TestStations(BaseAsyncHTTPTestCase):
    def test_add_station(self):
        session = self.ensure_login()
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
        response_latitude = response_body.get('latitude')
        latitude = float(response_latitude)
        response_longitude = response_body.get('longitude')
        longitude = float(response_longitude)
        self.assertEqual(lat, latitude)
        self.assertEqual(lon, longitude)

    def test_add_station_invalid_lat(self):
        session = self.ensure_login()
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
        session = self.ensure_login()
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
        stations = self.ensure_stations(45)
        session = self.ensure_login()
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
        response_body = json.loads(response.body.decode())
        station = self.closest_station(stations, lat, lon)
        self.assertEqual(station.station_id, response_body.get('station_id'))
