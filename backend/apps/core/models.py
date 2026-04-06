from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet 단위 soft delete 지원
    """

    def delete(self):
        return super().update(
            is_deleted=True,
            deleted_at=timezone.now(),
        )

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    기본 매니저
    - 삭제되지 않은 데이터만 조회
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db,
        ).filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    전체 조회 매니저
    - 삭제된 데이터 포함
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db,
        )


class SoftDeleteModel(models.Model):
    """
    공통 soft delete 추상 모델
    """

    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="삭제 일시")

    # 기본 조회는 살아있는 데이터만
    objects = SoftDeleteManager()

    # 관리자/복구용 전체 조회
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        기본 delete()는 물리 삭제가 아니라 논리 삭제
        """
        if self.is_deleted:
            return

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """
        진짜 물리 삭제가 필요할 때만 사용
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        삭제 복구
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])
