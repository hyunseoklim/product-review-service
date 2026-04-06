from django.contrib import admin
from .models import Review, ReviewImage, ReviewAI


@admin.action(description="선택한 리뷰 복구")
def restore_reviews(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


@admin.action(description="선택한 리뷰 완전 삭제")
def hard_delete_reviews(modeladmin, request, queryset):
    for obj in queryset:
        obj.hard_delete()


@admin.action(description="선택한 리뷰 삭제(논리 삭제)")
def soft_delete_reviews(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


class ReviewAIInline(admin.StackedInline):
    model = ReviewAI
    extra = 0
    can_delete = False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "user",
        "rating",
        "is_public",
        "is_deleted",
        "deleted_at",
        "created_at",
    ]
    list_filter = [
        "is_public",
        "is_deleted",
        "created_at",
    ]
    search_fields = ["content", "product__name", "user__username"]
    actions = [soft_delete_reviews, restore_reviews, hard_delete_reviews]
    inlines = [ReviewImageInline, ReviewAIInline]

    def get_queryset(self, request):
        # 삭제된 리뷰도 관리자 페이지에서 보이게 all_objects 사용
        return Review.all_objects.select_related("user", "product").all()

    def delete_model(self, request, obj):
        # 관리자 상세 페이지에서 delete 시 soft delete
        obj.delete()

    def delete_queryset(self, request, queryset):
        # 관리자 목록에서 여러 개 삭제해도 soft delete
        for obj in queryset:
            obj.delete()


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ["id", "review", "created_at"]


@admin.register(ReviewAI)
class ReviewAIAdmin(admin.ModelAdmin):
    list_display = ["id", "review", "sentiment", "confidence", "created_at"]
