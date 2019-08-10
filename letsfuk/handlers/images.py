from letsfuk.decorators import (
    check_session, image_endpoint_wrapper,
    map_exception
)
from letsfuk.errors import NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.s3 import S3Manager, KeyNotFound


class ImagesHandler(BaseHandler):
    @image_endpoint_wrapper()
    @map_exception(out_of=KeyNotFound, make=NotFound)
    @check_session()
    def get(self):
        key = self.request.params.get('key')
        data = S3Manager.get(key)
        return data, 200
