from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.reviews.models import Review

from .models import (
    ReviewLike,
    ReviewBookmark,
    ReviewComment,
    ReviewReport,
)

from .serializers import (
    ReviewCommentSerializer,
    ReviewReportSerializer,
)


# [10번에서 추가]
# 리뷰 좋아요 토글 APIView 추가
class ReviewLikeToggleAPIView(APIView):
    """
    리뷰 좋아요 토글 API

    기능
    - 이미 좋아요가 있으면 삭제 (좋아요 취소)
    - 없으면 생성 (좋아요 추가)

    요청 방식
    POST /reviews/{review_id}/like/
    """

    # [10번에서 추가] 로그인 사용자만 좋아요 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):

        # [10번에서 추가] review_id로 대상 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 이미 좋아요가 있으면 가져오고, 없으면 생성
        obj, created = ReviewLike.objects.get_or_create(
            review=review,
            user=request.user
        )

        # [10번에서 추가] 이미 존재하면 좋아요 취소
        if not created:
            obj.delete()
            liked = False
        else:
            # [10번에서 추가] 새로 생성되면 좋아요 상태 True
            liked = True

        # [10번에서 추가] 현재 리뷰의 전체 좋아요 개수 반환
        count = ReviewLike.objects.filter(review=review).count()

        return Response(
            {
                "liked": liked,
                "like_count": count,
            },
            status=status.HTTP_200_OK
        )


# [10번에서 추가]
# 리뷰 북마크 토글 APIView 추가
class ReviewBookmarkToggleAPIView(APIView):
    """
    리뷰 북마크 토글 API

    기능
    - 북마크 추가 / 북마크 취소
    """

    # [10번에서 추가] 로그인 사용자만 북마크 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):

        # [10번에서 추가] 대상 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 북마크가 있으면 가져오고, 없으면 생성
        obj, created = ReviewBookmark.objects.get_or_create(
            review=review,
            user=request.user
        )

        # [10번에서 추가] 이미 있으면 북마크 취소
        if not created:
            obj.delete()
            bookmarked = False
        else:
            bookmarked = True

        # [10번에서 추가] 현재 리뷰의 전체 북마크 수 계산
        count = ReviewBookmark.objects.filter(review=review).count()

        return Response(
            {
                "bookmarked": bookmarked,
                "bookmark_count": count,
            },
            status=status.HTTP_200_OK
        )


# [10번에서 추가]
# 리뷰 댓글 생성 APIView 추가
class ReviewCommentCreateAPIView(APIView):
    """
    리뷰 댓글 생성 API

    요청
    POST /reviews/{review_id}/comments/

    body
    {
        "content": "댓글 내용"
    }
    """

    # [10번에서 추가] 로그인 사용자만 댓글 작성 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):

        # [10번에서 추가] 댓글 대상 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 요청 body에서 댓글 내용 추출
        content = request.data.get("content", "").strip()

        # [10번에서 추가] 빈 댓글 방지
        if not content:
            return Response(
                {"detail": "내용이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # [10번에서 추가] 댓글 생성
        comment = ReviewComment.objects.create(
            review=review,
            user=request.user,
            content=content
        )

        # [10번에서 추가] serializer로 응답 데이터 변환
        serializer = ReviewCommentSerializer(comment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# [10번에서 추가]
# 리뷰 댓글 목록 조회 APIView 추가
class ReviewCommentListAPIView(APIView):
    """
    리뷰 댓글 목록 조회 API

    요청
    GET /reviews/{review_id}/comments/
    """

    # [10번에서 추가] 댓글 조회는 비로그인 사용자도 가능
    permission_classes = [AllowAny]

    def get(self, request, review_id):

        # [10번에서 추가] 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 해당 리뷰의 댓글을 최신순으로 조회
        comments = ReviewComment.objects.filter(
            review=review
        ).order_by("-created_at")

        # [10번에서 추가] 여러 개 댓글 직렬화
        serializer = ReviewCommentSerializer(comments, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# [10번에서 추가]
# 리뷰 댓글 수정 / 삭제 APIView 추가
class ReviewCommentDetailAPIView(APIView):
    """
    리뷰 댓글 수정 / 삭제 API

    수정
    PATCH /comments/{comment_id}/

    삭제
    DELETE /comments/{comment_id}/
    """

    # [10번에서 추가] 로그인 사용자만 수정/삭제 가능
    permission_classes = [IsAuthenticated]

    def patch(self, request, comment_id):

        # [10번에서 추가] 수정 대상 댓글 조회
        comment = get_object_or_404(ReviewComment, id=comment_id)

        # [10번에서 추가] 본인 댓글만 수정 가능
        if comment.user != request.user:
            return Response(
                {"detail": "본인 댓글만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        # [10번에서 추가] 수정할 내용 추출
        content = request.data.get("content", "").strip()

        # [10번에서 추가] 빈 내용 수정 방지
        if not content:
            return Response(
                {"detail": "내용이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # [10번에서 추가] 댓글 내용 수정 후 저장
        comment.content = content
        comment.save()

        serializer = ReviewCommentSerializer(comment)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, comment_id):

        # [10번에서 추가] 삭제 대상 댓글 조회
        comment = get_object_or_404(ReviewComment, id=comment_id)

        # [10번에서 추가] 본인 댓글만 삭제 가능
        if comment.user != request.user:
            return Response(
                {"detail": "본인 댓글만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        # [10번에서 추가] 댓글 삭제
        comment.delete()

        return Response(
            {"detail": "댓글이 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT
        )


# [10번에서 추가]
# 리뷰 신고 생성 APIView 추가
class ReviewReportCreateAPIView(APIView):
    """
    리뷰 신고 생성 API

    요청
    POST /reviews/{review_id}/report/

    body
    {
        "reason": "스팸 리뷰"
    }
    """

    # [10번에서 추가] 로그인 사용자만 신고 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):

        # [10번에서 추가] 신고 대상 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 신고 사유 추출
        reason = request.data.get("reason", "").strip()

        # [10번에서 추가] 신고 사유 없으면 오류
        if not reason:
            return Response(
                {"detail": "신고 사유가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # [10번에서 추가] 신고 생성
        report = ReviewReport.objects.create(
            review=review,
            user=request.user,
            reason=reason
        )

        serializer = ReviewReportSerializer(report)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# [10번에서 추가]
# 리뷰 신고 목록 조회 APIView 추가
class ReviewReportListAPIView(APIView):
    """
    리뷰 신고 목록 조회 API
    (관리자 확인용)

    GET /reviews/{review_id}/reports/
    """

    # [10번에서 추가] 현재 문서 기준으로 로그인 필요
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id):

        # [10번에서 추가] 리뷰 조회
        review = get_object_or_404(Review, id=review_id)

        # [10번에서 추가] 해당 리뷰의 신고 목록 조회
        reports = ReviewReport.objects.filter(
            review=review
        ).order_by("-created_at")

        serializer = ReviewReportSerializer(reports, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )