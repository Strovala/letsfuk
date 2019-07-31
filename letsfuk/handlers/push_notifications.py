from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    resolve_user,
    map_exception
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.push_notifications import (
    PushNotifications,
    InvalidPayload, SubscriberNotFound
)


class PushSubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidPayload, make=BadRequest)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        PushNotifications.verify_payload(self.request.body)
        subscriber = PushNotifications.subscribe(
            self.request.user, self.request.body
        )
        return subscriber.to_dict(), 201


class PushUnsubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=SubscriberNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        PushNotifications.unsubscribe(
            self.request.user, self.request.body
        )
        return {}, 204
