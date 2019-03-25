import os

import inject
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from tornado_sqlalchemy import make_session_factory

from letsfuk import ioc
from letsfuk.handlers import InfoView
from letsfuk.handlers.auth import LoginHandler, LogoutHandler
from letsfuk.handlers.users import UsersHandler

define('port', default=8888, help='port to listen on')
factory = make_session_factory(os.environ.get('DATABASE_URL', ''))


def make_app():
    return Application([
        ('/', InfoView),
        ('/auth/login', LoginHandler),
        ('/auth/logout', LogoutHandler),
        ('/users', UsersHandler),
    ],
        session_factory=factory
    )


def main():
    """Construct and serve the tornado application."""
    inject.configure(ioc.configuration)
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print('Listening on http://localhost:%i' % options.port)
    IOLoop.current().start()


main()
