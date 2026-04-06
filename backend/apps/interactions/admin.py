from django.contrib import admin
from .models import ReviewLike, ReviewBookmark, ReviewComment, ReviewReport


admin.site.register(ReviewLike)
admin.site.register(ReviewBookmark)
admin.site.register(ReviewComment)
admin.site.register(ReviewReport)