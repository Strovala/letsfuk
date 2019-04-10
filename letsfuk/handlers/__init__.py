import json

from sys import exc_info

from tornado.web import RequestHandler, HTTPError
from tornado_sqlalchemy import SessionMixin


class BaseHandler(RequestHandler, SessionMixin):
    """Base view for this application."""

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "session-id, content-type")
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

    def write_error(self, status_code, **kwargs):
        _, exc_obj, _ = exc_info()
        if isinstance(exc_obj, HTTPError):
            self.set_status(status_code)
            response = json.dumps({
                "error_message": str(exc_obj)
            })
            self.write(response)
            self.finish()
            # Maybe here we need return -\0/-
        super(BaseHandler, self).write_error(status_code, **kwargs)


class DefaultHandler(BaseHandler):
    # Override prepare() instead of get() to cover all possible HTTP methods.
    def prepare(self):
        self.set_status(404)
        response = json.dumps({
            "error_message": "Route not found"
        })
        self.write(response)
        self.finish()
