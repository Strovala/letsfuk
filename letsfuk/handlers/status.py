import logging

from letsfuk.decorators import endpoint_wrapper
from letsfuk.handlers import BaseHandler

logger = logging.getLogger(__name__)


class StatusHandler(BaseHandler):
    @endpoint_wrapper()
    def get(self):
        logger.info("I'm alive, Letsfuk!")
        return "I'm alive, Letsfuk!", 200
