import json

from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin


class BaseHandler(RequestHandler, SessionMixin):
    """Base view for this application."""

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        if isinstance(data, str):
            data = {
                "message": data
            }
        self.set_status(status)
        self.write(json.dumps(data))


class InfoView(BaseHandler):
    """Only allow GET requests."""
    SUPPORTED_METHODS = ["GET"]

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self):
        """List of routes for this API."""
        routes = {
            'register': 'POST /users',
            'login': 'POST /auth/login',
            'logout': 'POST /auth/logout',
            "get user by username": 'GET /users/<username>',
        }
        self.write(json.dumps(routes))
