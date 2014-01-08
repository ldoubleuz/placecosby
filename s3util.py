from storages.backends.s3boto import S3BotoStorage
from django.conf import settings

StaticStorage = lambda: S3BotoStorage(location='staticfiles', 
                                      bucket=settings.AWS_STORAGE_BUCKET_NAME)
MediaStorage = lambda: S3BotoStorage(location='media',
                                     bucket=settings.AWS_STORAGE_BUCKET_NAME)