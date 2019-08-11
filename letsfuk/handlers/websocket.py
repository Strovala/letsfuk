import json
import logging

from tornado.websocket import WebSocketHandler

logger = logging.getLogger(__name__)


class MessageWebSocketHandler(WebSocketHandler):
    live_web_sockets = dict()

    def check_origin(self, origin):
        return True

    def open(self):
        self.set_nodelay(True)

    def on_message(self, data):
        message = json.loads(data)
        if isinstance(message, dict):
            message_type = message.get('event')
            if message_type is not None:
                if message_type == 'connect':
                    data = message.get('data')
                    user_id = data.get('id')
                    self.live_web_sockets[user_id] = self
                    logger.info(
                        "Web socket opened for user_id: {}".format(user_id)
                    )

    def on_close(self):
        for user_id in self.live_web_sockets:
            ws = self.live_web_sockets[user_id]
            if ws == self:
                _ = self.live_web_sockets.pop(user_id)
                logger.info(
                    "Web socket closed for user_id: {}".format(user_id)
                )
                break

    @classmethod
    def send_message(cls, user_id, event='message', data=None):
        web_socket = cls.live_web_sockets.get(user_id)
        if web_socket is not None:
            web_socket.write_message({
                "event": event,
                "data": data
            })
            logger.info(
                "Sent message to user_id: {}, event: {}, data: {}".format(
                    user_id, event, data
                )
            )
