import uuid

import boto3
import inject
from botocore.exceptions import ClientError
from letsfuk import Config


class InvalidPayload(Exception):
    pass


class S3ClientError(Exception):
    pass


class KeyNotFound(Exception):
    pass


class S3Manager(object):
    @classmethod
    def verify_key(cls, params):
        key = params.get('key')
        if key is None:
            raise InvalidPayload("You must provide a key!")
        if type(key) != str:
            raise InvalidPayload("Image key must be string!")
        if key == "":
            raise InvalidPayload("Image key must not be empty!")

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
            raise S3ClientError(e)
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
        # TODO: Consider changing this username to user id
        # maybe username and email will not be unique anymore
        # Also username not case sensitive
        key = "{}/{}".format(user.username, key_uuid)
        return key

    @classmethod
    def delete(cls, object_name):
        s3 = boto3.resource("s3")
        config = inject.instance(Config)
        bucket_name = config.get('s3_bucket', 'letsfuk')
        obj = s3.Object(bucket_name, object_name)
        obj.delete()

    @classmethod
    def get(cls, params):
        object_name = params.get('key')
        s3 = boto3.resource("s3")
        config = inject.instance(Config)
        bucket_name = config.get('s3_bucket', 'letsfuk')
        obj = s3.Object(bucket_name, object_name)
        try:
            return obj.get()['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise KeyNotFound(
                    "Provided key: {} not found".format(object_name)
                )
