import json

from datetime import datetime

from letsfuk.tests import BaseAsyncHTTPTestCase


class TestMessages(BaseAsyncHTTPTestCase):
    def prepare_for_sending_message_to_station(self):
        session, user = self.ensure_login()
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        station = self.add_station(lat=lat, lon=lon)
        _ = self.subscribe(station.station_id, user.user_id)
        return session, user, station

    def prepare_for_sending_message_to_user(self):
        session, user = self.ensure_login()
        receiver = self.ensure_register()
        lat = self.generator.latitude.generate()
        lon = self.generator.longitude.generate()
        station = self.add_station(lat=lat, lon=lon)
        _ = self.subscribe(station.station_id, user.user_id)
        _ = self.subscribe(station.station_id, receiver.user_id)
        return session, user, receiver, station

    def test_add_message_to_station(self):
        session, user, station = self.prepare_for_sending_message_to_station()
        text = self.generator.text.generate()
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        response = self.fetch(
            '/messages/{}'.format(station.station_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(station.station_id, response_body.get('receiver_id'))
        self.assertEqual(now, response_body.get('sent_at'))

    def test_add_message_to_station_invalid_station(self):
        session, _, _ = self.prepare_for_sending_message_to_station()
        text = self.generator.text.generate()
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        fake_station_id = self.generator.uuid.generate()
        response = self.fetch(
            '/messages/{}'.format(fake_station_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 404)

    def test_add_message_to_user(self):
        session, _, receiver, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        response = self.fetch(
            '/messages/{}'.format(receiver.user_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(receiver.user_id, response_body.get('receiver_id'))
        self.assertEqual(now, response_body.get('sent_at'))

    def test_add_message_to_user_invalid_user(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        fake_user_id = self.generator.uuid.generate()
        response = self.fetch(
            '/messages/{}'.format(fake_user_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 404)

    def test_add_message_unauthorized(self):
        _, user, station = self.prepare_for_sending_message_to_station()
        text = self.generator.text.generate()
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        response = self.fetch(
            '/messages/{}'.format(station.station_id),
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 401)

    def test_add_message_too_long_text(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        for _ in range(4):
            text += text
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        fake_station_id = self.generator.uuid.generate()
        response = self.fetch(
            '/messages/{}'.format(fake_station_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_add_message_invalid_time(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        for _ in range(4):
            text += text
        now = str(datetime.now())
        body = {
            "text": text,
            "sent_at": now
        }
        fake_station_id = self.generator.uuid.generate()
        response = self.fetch(
            '/messages/{}'.format(fake_station_id),
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)
