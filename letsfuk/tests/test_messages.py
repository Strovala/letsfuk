import json

from datetime import datetime

from letsfuk.tests import BaseAsyncHTTPTestCase


class TestMessages(BaseAsyncHTTPTestCase):
    def prepare_for_sending_message_to_station(self):
        session, user = self.ensure_login()
        station = self.add_station()
        _ = self.subscribe(station.station_id, user.user_id)
        return session, user, station

    def prepare_for_sending_message_to_user(self):
        session, user = self.ensure_login()
        receiver = self.ensure_register()
        station = self.add_station()
        _ = self.subscribe(station.station_id, user.user_id)
        _ = self.subscribe(station.station_id, receiver.user_id)
        return session, user, receiver, station

    def test_add_message_to_station(self):
        session, user, station = self.prepare_for_sending_message_to_station()
        text = self.generator.text.generate()
        body = {
            "text": text
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
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(station.station_id, response_body.get('receiver_id'))
        self.assertEqual(user.user_id, œresponse_body.get('sender_id'))

    def test_add_message_to_user(self):
        session, user, receiver, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        body = {
            "text": text,
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
        self.assertEqual(text, response_body.get('text'))
        self.assertEqual(receiver.user_id, response_body.get('receiver_id'))
        self.assertEqual(user.user_id, response_body.get('sender_id'))

    def test_add_message_to_user_invalid_user(self):
        session, _, _, _ = self.prepare_for_sending_message_to_user()
        text = self.generator.text.generate()
        fake_user_id = self.generator.uuid.generate()
        body = {
            "text": text,
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
        body = {
            "text": text
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
        body = {
            "text": text
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

    def test_get_station_chat(self):
        session, user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        messages = self.make_station_chat(station)
        offset, limit = 5, 10
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                station.station_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        receiver_id = response_body.get('receiver_id')
        self.assertEqual(station.station_id, receiver_id)
        end = limit + offset
        if end > len(messages):
            end = len(messages)
        if offset >= len(messages):
            messages = []
        else:
            messages = messages[offset:end]
        response_messages = response_body.get('messages')
        self.assertEqual(len(response_messages), len(messages))
        for i in range(len(response_messages)):
            response_message = response_messages[i]
            message = messages[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )

    def test_get_private_chat(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        _, third_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        self.subscribe(station.station_id, third_user.user_id)
        messages = self.make_private_chat(user, another_user)
        _ = self.make_private_chat(user, third_user)
        offset, limit = 5, 10
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        receiver_id = response_body.get('receiver_id')
        self.assertEqual(another_user.user_id, receiver_id)
        end = limit + offset
        if end > len(messages):
            end = len(messages)
        if offset >= len(messages):
            messages = []
        else:
            messages = messages[offset:end]
        response_messages = response_body.get('messages')
        self.assertEqual(len(response_messages), len(messages))
        for i in range(len(response_messages)):
            response_message = response_messages[i]
            message = messages[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )

    def test_chat_default_limit_offset(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        messages = self.make_private_chat(user, another_user)
        offset, limit = 0, 20
        response = self.fetch(
            '/messages/{}?'.format(
                another_user.user_id
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        receiver_id = response_body.get('receiver_id')
        self.assertEqual(another_user.user_id, receiver_id)
        end = limit + offset
        if end > len(messages):
            end = len(messages)
        if offset >= len(messages):
            messages = []
        else:
            messages = messages[offset:end]
        response_messages = response_body.get('messages')
        self.assertEqual(len(response_messages), len(messages))
        for i in range(len(response_messages)):
            response_message = response_messages[i]
            message = messages[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )

    def test_chat_limit_goes_out_of_bounds(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        messages = self.make_private_chat(user, another_user)
        offset, limit = 19, 10
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        receiver_id = response_body.get('receiver_id')
        self.assertEqual(another_user.user_id, receiver_id)
        end = limit + offset
        if end > len(messages):
            end = len(messages)
        if offset >= len(messages):
            messages = []
        else:
            messages = messages[offset:end]
        response_messages = response_body.get('messages')
        self.assertEqual(len(response_messages), len(messages))
        for i in range(len(response_messages)):
            response_message = response_messages[i]
            message = messages[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )

    def test_chat_offset_goes_out_of_bounds(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        messages = self.make_private_chat(user, another_user)
        offset, limit = 30, 10
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        receiver_id = response_body.get('receiver_id')
        self.assertEqual(another_user.user_id, receiver_id)
        end = limit + offset
        if end > len(messages):
            end = len(messages)
        if offset >= len(messages):
            messages = []
        else:
            messages = messages[offset:end]
        response_messages = response_body.get('messages')
        self.assertEqual(len(response_messages), len(messages))
        for i in range(len(response_messages)):
            response_message = response_messages[i]
            message = messages[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )

    def test_chat_unauthorized(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        _ = self.make_private_chat(user, another_user)
        offset, limit = 'random', 5
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET"
        )
        self.assertEqual(response.code, 401)

    def test_chat_invalid_offset(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        _ = self.make_private_chat(user, another_user)
        offset, limit = 'random', 5
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_chat_invalid_limit(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        _ = self.make_private_chat(user, another_user)
        offset, limit = 5, 6.9
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                another_user.user_id, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 400)

    def test_chat_invalid_receiver(self):
        session, user = self.ensure_login()
        _, another_user = self.ensure_login()
        station = self.add_station()
        self.subscribe(station.station_id, user.user_id)
        self.subscribe(station.station_id, another_user.user_id)
        _ = self.make_private_chat(user, another_user)
        offset, limit = 5, 10
        random_receiver = self.generator.uuid.generate()
        response = self.fetch(
            '/messages/{}?offset={}&limit={}'.format(
                random_receiver, offset, limit
            ),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 404)

    def test_get_chats(self):
        session, station_chat, private_chats = self.make_chats()
        offset, limit = 0, 10
        response = self.fetch(
            '/messages?offset={}&limit={}'.format(offset, limit),
            method="GET",
            headers={
                "session-id": session.session_id
            }
        )
        self.assertEqual(response.code, 200)
        response_body = json.loads(response.body.decode())
        response_station_chat_dict = response_body.get('station_chat')
        self.assertIsNotNone(response_station_chat_dict)
        response_station_chat = response_station_chat_dict.get('messages')
        self.assertIsNotNone(response_station_chat)
        self.assertEqual(len(station_chat), len(response_station_chat))
        for i in range(len(response_station_chat)):
            message = station_chat[i]
            response_message = response_station_chat[i]
            self.assertEqual(message.text, response_message.get('text'))
            self.assertEqual(
                str(message.sent_at), response_message.get('sent_at')
            )
        response_private_chats = response_body.get('private_chats')
        self.assertIsNotNone(response_private_chats)
        end = limit + offset
        if end > len(private_chats):
            end = len(private_chats)
        if offset >= len(private_chats):
            private_chat = []
        else:
            private_chat = private_chats[offset:end]
        self.assertEqual(len(private_chats), len(response_private_chats))
        for i in range(len(response_private_chats)):
            chat = private_chat[i]
            response_chat = response_private_chats[i]
            self.assertEqual(
                chat.get('receiver_id'),
                response_chat.get('receiver_id')
            )
            messages = chat.get('messages')
            response_messages = response_chat.get('messages')
            self.assertEqual(len(messages), len(response_messages))
            for j in range(len(response_messages)):
                message = messages[i]
                response_message = response_messages[i]
                self.assertEqual(message.text, response_message.get('text'))
                self.assertEqual(
                    str(message.sent_at), response_message.get('sent_at')
                )

    def test_get_chats_unauthorized(self):
        _, station_chat, private_chats = self.make_chats()
        offset, limit = 0, 10
        response = self.fetch(
            '/messages?offset={}&limit={}'.format(offset, limit),
            method="GET",
        )
        self.assertEqual(response.code, 401)
