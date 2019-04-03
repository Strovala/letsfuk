import json

from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin


class BaseHandler(RequestHandler, SessionMixin):
    """Base view for this application."""

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "session-id")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        if isinstance(data, str):
            data = {
                "message": data
            }
        self.set_status(status)
        self.write(json.dumps(data))

    def send_error(self, status_code=500, **kwargs):
        # super(BaseHandler, self).send_error(status_code, **kwargs)
        print("Ajddeee")
        print(status_code)
