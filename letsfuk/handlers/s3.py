from letsfuk.decorators import (
    check_session, endpoint_wrapper, resolve_body, map_exception,
    resolve_user)
from letsfuk.errors import NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.s3 import S3Manager
from letsfuk.models.user import UserNotFound


class S3PresignUploadHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self):
        key = S3Manager.generate_key_for_user(self.request.user)
        response = S3Manager.create_presigned_url_upload(key)
        return {
            "url": response,
            "key": key
        }, 200
