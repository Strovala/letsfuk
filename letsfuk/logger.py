import logging
import os
import time

logger = logging.getLogger(__name__)


def configure_develop_logging(application):
    _configure_logging(
        application,
        production=False
    )


def configure_production_logging(application):
    _configure_logging(
        application,
        production=True
    )


def _configure_logging(application, production):
    app_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
    formatter_string = (
        "{}: %(asctime)s %(levelname)s: "
        "%(message)s [%(name)s:%(lineno)d]".format(application)
    )
    datefmt_string = "%Y.%m.%d %H:%M:%S"
    logging.basicConfig(
        level=logging.DEBUG if not production else logging.INFO,
        format=formatter_string,
        datefmt=datefmt_string,
        filename='{}/{}.log'.format(app_dir, application),
        filemode='a'
    )
    if not production:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(
            formatter_string, datefmt_string
        ))
        logging.getLogger('').addHandler(console)
    logger.info(
        'Configuring logging for %s completed.',
        'production' if production else 'development'
    )
