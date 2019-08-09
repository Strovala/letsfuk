import uuid

import boto3
import inject
from botocore.exceptions import ClientError

from letsfuk import Config


class S3Manager(object):
    @classmethod
    def _create_presigned_url(
            cls, object_name, method='get_object', expiration=60
    ):
        # Generate a presigned URL for the S3 object
        config = inject.instance(Config)
        bucket_name = config.get('s3_bucket', 'letsfuk')
        reagion_name = config.get('s3_region', 'eu-west-2')
        session = boto3.session.Session(region_name=reagion_name)
        s3_client = session.client('s3', config= boto3.session.Config(
            signature_version='s3v4'
        ))
        try:
            response = s3_client.generate_presigned_url(
                method,
                Params={
                    'Bucket': bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
        except ClientError as e:
            print(e)
            return None
        return response

    @classmethod
    def create_presigned_url_upload(cls, object_name, expiration=60):
        return cls._create_presigned_url(
            object_name, method='put_object', expiration=expiration
        )

    @classmethod
    def create_presigned_url_get(cls, object_name, expiration=60):
        return cls._create_presigned_url(
            object_name, expiration=expiration
        )

    @classmethod
    def generate_key_for_user(cls, user):
        key_uuid = str(uuid.uuid4())
        key = "{}/{}".format(user.username, key_uuid)
        return key

    @classmethod
    def delete(cls, object_name):
        s3 = boto3.resource("s3")
        config = inject.instance(Config)
        bucket_name = config.get('s3_bucket', 'letsfuk')
        obj = s3.Object(bucket_name, object_name)
        obj.delete()
