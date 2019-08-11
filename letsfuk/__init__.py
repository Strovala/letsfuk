import argparse
import ssl
import logging
import inject
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from tornado_sqlalchemy import make_session_factory

from letsfuk import ioc
from letsfuk.config import Config
from letsfuk.db import Base
from letsfuk.handlers import DefaultHandler
from letsfuk.handlers.auth import LoginHandler, LogoutHandler
from letsfuk.handlers.images import ImagesHandler
from letsfuk.handlers.messages import (
    MessagesHandler, ChatMessagesHandler, UnreadMessagesHandler
)
from letsfuk.handlers.push_notifications import (
    PushSubscribeHandler, PushUnsubscribeHandler,
    PushCheckHandler)
from letsfuk.handlers.s3 import S3PresignUploadHandler
from letsfuk.handlers.stations import StationsHandler, SubscribeHandler
from letsfuk.handlers.users import UsersHandler, UserHandler, WhoAmIHandler
from letsfuk.handlers.websocket import MessageWebSocketHandler
from letsfuk.logger import (
    configure_develop_logging, configure_production_logging
)

uuid_regex = (
    "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}"
    "\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
)

logger = logging.getLogger(__name__)


def make_app():
    config = inject.instance(Config)
    debug = config.get('debug')
    database_url = config.get('database_url')
    factory = make_session_factory(database_url)
    return Application([
        ('/auth/login?', LoginHandler),
        ('/auth/logout?', LogoutHandler),
        ('/whoami?', WhoAmIHandler),
        ('/users?', UsersHandler),
        ('/users/({})/?'.format(uuid_regex), UserHandler),
        ('/users/({})/station/?'.format(uuid_regex), SubscribeHandler),
        ('/stations/?', StationsHandler),
        ('/stations/subscribe/?', SubscribeHandler),
        ('/messages/?', MessagesHandler),
        ('/messages/({})/?'.format(uuid_regex), ChatMessagesHandler),
        ('/messages/unreads/reset/?', UnreadMessagesHandler),
        ('/push-notifications/check/?', PushCheckHandler),
        ('/push-notifications/subscribe/?', PushSubscribeHandler),
        (
            '/push-notifications/unsubscribe/?',
            PushUnsubscribeHandler
        ),
        ('/websocket/?', MessageWebSocketHandler),
        ('/presign/upload/?', S3PresignUploadHandler),
        ('/images/?', ImagesHandler),
    ],
        default_handler_class=DefaultHandler,
        session_factory=factory,
        debug=debug
    )


def migrate():
    inject.configure(ioc.configuration)
    engine = inject.instance('db_engine')
    Base.metadata.create_all(engine)
    print("Migration successful!")


def main():
    """Construct and serve the tornado application."""
    inject.configure(ioc.configuration)
    app = make_app()
    cfg = inject.instance(Config)
    ssl_ctx = None
    development = cfg.get('development', False)
    if development:
        configure_develop_logging('letsfuk')
    else:
        configure_production_logging('letsfuk')
    if not development:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(cfg.get('crt'), cfg.get('key'))
    http_server = HTTPServer(
        app,
        ssl_options=ssl_ctx
    )
    port = cfg.get('port', 8888)
    http_server.listen(port)
    logger.info('Listening on http://localhost:{}'.format(port))
    IOLoop.current().start()


parser = argparse.ArgumentParser(description='Process command.')
parser.add_argument('--execute', action="store")
args = parser.parse_args()
if args.execute == 'run':
    define('port', default=8888, help='port to listen on')
    main()
elif args.execute == 'migrate':
    migrate()
