from django.urls import path

# interactions 앱에서 사용하는 APIView import
from .views import (
    ReviewLikeToggleAPIView,        # 리뷰 좋아요 토글 API
    ReviewBookmarkToggleAPIView,    # 리뷰 북마크 토글 API
    ReviewCommentCreateAPIView,     # 리뷰 댓글 생성 API
    ReviewCommentListAPIView,       # 리뷰 댓글 목록 조회 API
    ReviewCommentDetailAPIView,     # 리뷰 댓글 수정 / 삭제 API
    ReviewReportCreateAPIView,      # 리뷰 신고 생성 API
    ReviewReportListAPIView,        # 리뷰 신고 목록 조회 API
)

# interactions 앱의 URL 패턴 정의
urlpatterns = [

    # ---------------------------------------------------------
    # 리뷰 좋아요 토글
    #
    # 기능
    # - 이미 좋아요가 있으면 취소
    # - 없으면 좋아요 추가
    #
    # 요청 방식
    # POST /interaction/like/<review_id>/
    #
    # 예시
    # POST /interaction/like/5/
    # → review id=5에 좋아요 토글
    # ---------------------------------------------------------
    path(
        "like/<int:review_id>/",
        ReviewLikeToggleAPIView.as_view(),
        name="review-like-toggle"
    ),


    # ---------------------------------------------------------
    # 리뷰 북마크 토글
    #
    # 기능
    # - 북마크 추가 / 취소
    #
    # 요청 방식
    # POST /interaction/bookmark/<review_id>/
    #
    # 예시
    # POST /interaction/bookmark/5/
    # ---------------------------------------------------------
    path(
        "bookmark/<int:review_id>/",
        ReviewBookmarkToggleAPIView.as_view(),
        name="review-bookmark-toggle"
    ),


    # ---------------------------------------------------------
    # 리뷰 댓글 등록
    #
    # 기능
    # - 특정 리뷰에 댓글 생성
    #
    # 요청 방식
    # POST /interaction/comment/<review_id>/
    #
    # body 예시
    # {
    #     "content": "좋은 리뷰네요!"
    # }
    # ---------------------------------------------------------
    path(
        "comment/<int:review_id>/",
        ReviewCommentCreateAPIView.as_view(),
        name="review-comment-create"
    ),


    # ---------------------------------------------------------
    # 리뷰 댓글 목록 조회
    #
    # 기능
    # - 특정 리뷰의 댓글 리스트 조회
    #
    # 요청 방식
    # GET /interaction/comments/<review_id>/
    #
    # 예시
    # GET /interaction/comments/5/
    # ---------------------------------------------------------
    path(
        "comments/<int:review_id>/",
        ReviewCommentListAPIView.as_view(),
        name="review-comment-list"
    ),


    # ---------------------------------------------------------
    # 리뷰 댓글 수정 / 삭제
    #
    # 기능
    # - 댓글 수정 (PATCH)
    # - 댓글 삭제 (DELETE)
    #
    # 요청 방식
    # PATCH /interaction/comment/detail/<comment_id>/
    # DELETE /interaction/comment/detail/<comment_id>/
    #
    # 예시
    # PATCH /interaction/comment/detail/10/
    # DELETE /interaction/comment/detail/10/
    # ---------------------------------------------------------
    path(
        "comment/detail/<int:comment_id>/",
        ReviewCommentDetailAPIView.as_view(),
        name="review-comment-detail"
    ),


    # ---------------------------------------------------------
    # 리뷰 신고 등록
    #
    # 기능
    # - 부적절한 리뷰 신고
    #
    # 요청 방식
    # POST /interaction/report/<review_id>/
    #
    # body 예시
    # {
    #     "reason": "광고성 리뷰"
    # }
    # ---------------------------------------------------------
    path(
        "report/<int:review_id>/",
        ReviewReportCreateAPIView.as_view(),
        name="review-report-create"
    ),


    # ---------------------------------------------------------
    # 리뷰 신고 목록 조회
    #
    # 기능
    # - 특정 리뷰에 대한 신고 목록 조회
    # - 관리자 확인용
    #
    # 요청 방식
    # GET /interaction/reports/<review_id>/
    #
    # 예시
    # GET /interaction/reports/5/
    # ---------------------------------------------------------
    path(
        "reports/<int:review_id>/",
        ReviewReportListAPIView.as_view(),
        name="review-report-list"
    ),
]