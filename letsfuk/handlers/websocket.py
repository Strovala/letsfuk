import json
from tornado.websocket import WebSocketHandler


class MessageWebSocketHandler(WebSocketHandler):
    live_web_sockets = dict()

    def check_origin(self, origin):
        return True

    def open(self):
        self.set_nodelay(True)

    def on_message(self, data):
        print(data)
        message = json.loads(data)
        if isinstance(message, dict):
            message_type = message.get('event')
            if message_type is not None:
                if message_type == 'connect':
                    data = message.get('data')
                    user_id = data.get('id')
                    self.live_web_sockets[user_id] = self
                    print("WebSocket opened for {}".format(user_id))

    def on_close(self):
        for user_id in self.live_web_sockets:
            ws = self.live_web_sockets[user_id]
            if ws == self:
                _ = self.live_web_sockets.pop(user_id)
                print("WebSocket closed for {}".format(user_id))
                break
