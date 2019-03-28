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
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        body = {
            "text": text,
            "sent_at": now_string
        }
        response = self.fetch(
            '/messages',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        sent_at = str(datetime.strptime(now_string, '%b %d %Y %H:%M'))
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(station.station_id, response_body.get('receiver_id'))
        self.assertEqual(user.user_id, response_body.get('sender_id'))
        self.assertEqual(sent_at, response_body.get('sent_at'))

    def test_add_message_to_user(self):
        session, user, receiver, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        body = {
            "text": text,
            "sent_at": now_string,
            "user_id": receiver.user_id
        }
        response = self.fetch(
            '/messages',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        sent_at = str(datetime.strptime(now_string, '%b %d %Y %H:%M'))
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(receiver.user_id, response_body.get('receiver_id'))
        self.assertEqual(user.user_id, response_body.get('sender_id'))
        self.assertEqual(sent_at, response_body.get('sent_at'))

    def test_add_message_to_user_invalid_user(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        fake_user_id = self.generator.uuid.generate()
        body = {
            "text": text,
            "sent_at": now_string,
            "user_id": fake_user_id
        }
        response = self.fetch(
            '/messages',
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
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        body = {
            "text": text,
            "sent_at": now_string
        }
        response = self.fetch(
            '/messages',
            method="POST",
            body=json.dumps(body).encode('utf-8')
        )
        self.assertEqual(response.code, 401)

    def test_add_message_too_long_text(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        for _ in range(4):
            text += text
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        body = {
            "text": text,
            "sent_at": now_string
        }
        response = self.fetch(
            '/messages',
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
        now = datetime.now()
        now_string = now.strftime('%b %d %Y %H:%M')
        body = {
            "text": text,
            "sent_at": now_string + "/"
        }
        response = self.fetch(
            '/messages',
            method="POST",
            body=json.dumps(body).encode('utf-8'),
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)
