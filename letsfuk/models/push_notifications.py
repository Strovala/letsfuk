import inject

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
