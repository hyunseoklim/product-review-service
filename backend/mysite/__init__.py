# [추가] Celery 앱을 Django 시작 시 함께 로드

from .celery import app as celery_app

__all__ = ("celery_app",)