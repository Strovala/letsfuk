from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user)
from letsfuk.handlers import BaseHandler
from letsfuk.models.message import Message


class MessageHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self, receiver_id):
        message = Message.add(
            self.request.body, receiver_id, self.request.user
        )
        return message.to_dict(), 201
