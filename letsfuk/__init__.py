import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from tornado_sqlalchemy import make_session_factory

from letsfuk.views import InfoView

define('port', default=8888, help='port to listen on')
factory = make_session_factory(os.environ.get('DATABASE_URL', ''))


def make_app():
    return Application([
        ('/', InfoView)
    ],
        session_factory=factory
    )


def main():
    """Construct and serve the tornado application."""
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print('Listening on http://localhost:%i' % options.port)
    IOLoop.current().start()


main()
