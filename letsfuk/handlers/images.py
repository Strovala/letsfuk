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
        S3Manager.verify_key(self.request.params)
        data = S3Manager.get(self.request.params)
        return data, 200
