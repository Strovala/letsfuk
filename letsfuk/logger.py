import logging
import logging.config
import time
from sys import platform

logger = logging.getLogger(__name__)

PRODUCTION_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "syslog": {
        "connection_type": "port",
        "host": "127.0.0.1",
        "port": 514
    },
    "formatters": {
        "verbose": {
            "format": "%(asctime)s.%(msecs)03d   "
                      "%(levelname)11s: %(message)s [%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)-11s - %(message)s [%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "audit": {
            "format": "%(message)s"
        },
        "syslog": {
            "format": "{}:   %(levelname)11s: %(message)s "
                      "[%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "syslog_audit": {
            "format": "{}-audit:   %(message)s",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        }
    },
    "handlers": {
        "syslog": {
            "level": "INFO",
            "formatter": "syslog",
            "class": "logging.handlers.SysLogHandler",
            "address": '/dev/log',
            "facility": "local1"
        },
        "syslog_audit": {
            "level": "INFO",
            "formatter": "syslog_audit",
            "class": "logging.handlers.SysLogHandler",
            "address": None,
            "facility": "local1"
        }
    },
    "loggers": {
        "audit": {
            "handlers": [
                "syslog_audit"
            ],
            "level": "INFO",
            "propagate": 0
        }
    },
    "root": {
        "handlers": [
            "syslog"
        ],
        "level": "INFO",
        "propagate": 1
    }
}

DEBUG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s.%(msecs)03d   "
                      "%(levelname)11s: %(message)s "
                      "[%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)-11s - %(message)s [%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "audit": {
            "format": "%(message)s"
        },
        "syslog": {
            "format": "{}:   %(levelname)11s: %(message)s "
                      "[%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        },
        "syslog_audit": {
            "format": "{}-audit:   %(message)s",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        }
    },
    "root": {
        "handlers": [
            "console"
        ],
        "level": "DEBUG",
        "propagate": 1
    }
}


def _merge_log_configs(config, new):
    # Merge top level keys
    if 'disable_existing_loggers' in new:
        config['disable_existing_loggers'] = new['disable_existing_loggers']
    # Merge nested keys
    if 'formatters' in new:
        if 'formatters' not in config:
            config['formatters'] = {}
        for formatter, data in new['formatters'].items():
            config['formatters'][formatter] = data
    if 'handlers' in new:
        if 'handlers' not in config:
            config['handlers'] = {}
        for handler, data in new['handlers'].items():
            config['handlers'][handler] = data
    if 'loggers' in new:
        if 'loggers' not in config:
            config['loggers'] = {}
        for logger, data in new['loggers'].items():
            config['loggers'][logger] = data
    if 'root' in new:
        if 'root' not in config:
            config['root'] = {}
        for item, data in new['root'].items():
            config['root'][item] = data
    if 'syslog' in new:
        if 'syslog' not in config:
            config['syslog'] = {}
        for item, data in new['syslog'].items():
            config['syslog'][item] = data
    return config


def configure_develop_logging(application, config=None):
    _configure_logging(
        application,
        production=False,
        basic_config=dict(DEBUG_CONFIG),
        override=config
    )


def configure_production_logging(application, config=None):
    _configure_logging(
        application,
        production=True,
        basic_config=dict(PRODUCTION_CONFIG),
        override=config
    )


def _configure_logging(application, production, basic_config, override=None):
    template = basic_config["formatters"]["syslog"]["format"]
    basic_config["formatters"]["syslog"]["format"] = template.format(
        application.lower())
    template = basic_config["formatters"]["syslog_audit"]["format"]
    basic_config["formatters"]["syslog_audit"]["format"] = template.format(
        application.lower())

    # Merge override if exists
    if override is not None:
        config = _merge_log_configs(basic_config, override)
    else:
        config = basic_config

    if production:
        # Define syslog connection
        if config['syslog']['connection_type'] == 'port':
            syslog_address = (config['syslog']['host'],
                              config['syslog']['port'])
        else:
            if platform == 'darwin':
                syslog_address = '/var/run/syslog'
            else:
                syslog_address = '/dev/log'

        config['handlers']['syslog']['address'] = syslog_address
        config['handlers']['syslog_audit']['address'] = syslog_address

    logging.Formatter.converter = time.gmtime
    # Configure logging
    logging.config.dictConfig(config)
    logger.info('Configuring logging for %s completed.',
                'production' if production else 'development')
