from storages.backends.s3 import S3Storage
import os

class StaticStorage(S3Storage):
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME_STATIC")
    location = "static"
    default_acl = None
    querystring_auth = False

class MediaStorage(S3Storage):
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME_MEDIA")
    location = "media"
    default_acl = None
    querystring_auth = False