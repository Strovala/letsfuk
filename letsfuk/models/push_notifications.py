import inject
import json
from pywebpush import webpush

from letsfuk import Config
from letsfuk.db.models import PushNotification as DbPushNotification


class InvalidPayload(Exception):
    pass


class SubscriberNotFound(Exception):
    pass


class PushNotifications(object):
    @classmethod
    def verify_payload(cls, payload):
        endpoint = payload.get('endpoint')
        if endpoint is None:
            raise InvalidPayload("Endpoint not provided!")
        keys = payload.get('keys')
        if keys is None:
            raise InvalidPayload("Keys not provided!")
        auth = keys.get('auth')
        if auth is None:
            raise InvalidPayload("Auth key not provided!")
        p256dh = keys.get('p256dh')
        if p256dh is None:
            raise InvalidPayload("p256dh key not provided!")

    @classmethod
    def subscribe(cls, user, payload):
        endpoint = payload.get('endpoint')
        keys = payload.get('keys')
        auth = keys.get('auth')
        p256dh = keys.get('p256dh')
        db = inject.instance('db')
        subscriber = DbPushNotification.subscribe(
            db, user.user_id, endpoint, auth, p256dh
        )
        return subscriber

    @classmethod
    def unsubscribe(cls, user, payload):
        endpoint = payload.get('endpoint')
        keys = payload.get('keys')
        auth = keys.get('auth')
        p256dh = keys.get('p256dh')
        db = inject.instance('db')
        subscriber = DbPushNotification.get(
            db, user.user_id, endpoint, auth, p256dh
        )
        if subscriber is None:
            raise SubscriberNotFound(
                "There is no subscription for user with user_id: {}".format(user.user_id)
            )
        _ = DbPushNotification.unsubscribe(db, subscriber)

    @classmethod
    def send(cls, device_browser, data):
        subscription_info = device_browser.to_dict()
        subscription_info.pop('user_id')
        json_data = json.dumps(data)
        config = inject.instance(Config)
        vapid_private_key = config.get('vapid_private_key')
        email = config.get('vapid_private_key')
        webpush(
            subscription_info,
            json_data,
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": 'mailto:{}'.format(email)}
        )

    @classmethod
    def send_to_user(cls, user_id, data):
        db = inject.instance('db')
        device_browsers = DbPushNotification.query_by_user_id(db, user_id)
        for device_browser in device_browsers:
            cls.send(device_browser, data)
