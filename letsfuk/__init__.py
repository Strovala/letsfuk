import os

import inject
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from tornado_sqlalchemy import make_session_factory

from config import Config
from letsfuk import ioc
from letsfuk.handlers import InfoView
from letsfuk.handlers.auth import LoginHandler, LogoutHandler
from letsfuk.handlers.users import UsersHandler, UserHandler

uuid_regex = (
    "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}"
    "\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
)


def make_app():
    config = inject.instance(Config)
    debug = config.get('debug')
    database_url = config.get('database_url')
    factory = make_session_factory(database_url)
    return Application([
        ('/', InfoView),
        ('/auth/login', LoginHandler),
        ('/auth/logout', LogoutHandler),
        ('/users', UsersHandler),
        ('/users/(\w+)?', UserHandler),
    ],
        session_factory=factory,
        debug=debug
    )


def main():
    """Construct and serve the tornado application."""
    inject.configure(ioc.configuration)
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print('Listening on http://localhost:%i' % options.port)
    IOLoop.current().start()


if __name__ == '__main__':
    define('port', default=8888, help='port to listen on')
    main()
