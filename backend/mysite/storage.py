from storages.backends.s3 import S3Storage
import os

class StaticStorage(S3Storage):
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME_STATIC")
    location = "static"
    default_acl = None
    querystring_auth = False
    region_name = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
    custom_domain = f"{os.getenv('AWS_STORAGE_BUCKET_NAME_STATIC')}.s3.{os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')}.amazonaws.com"

class MediaStorage(S3Storage):
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME_MEDIA")
    location = "media"
    default_acl = None
    querystring_auth = False
    region_name = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
    custom_domain = f"{os.getenv('AWS_STORAGE_BUCKET_NAME_MEDIA')}.s3.{os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')}.amazonaws.com"
