# [수정]
# 기존: from requests import RequestException
# 변경: requests.exceptions 에서 직접 import
from requests.exceptions import RequestException

# [추가]
# Celery 작업의 현재 상태 조회를 위해 AsyncResult import 추가
from celery.result import AsyncResult

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from apps.reviews.models import Review

from .serializers import (
    EmbeddingRequestSerializer,
    SimilarityRequestSerializer,
)

# [유지]
# Embedding / Similarity API는 여전히 FastAPI를 직접 호출
from .services import FastAPIClient

# [수정]
# 기존: ReviewSimilarityResult 를 import 해서 View 안에서 직접 저장했음
# 변경: 비동기 작업 상태 저장용 AIAnalysisTask import
from .models import AIAnalysisTask

# [추가]
# 실제 AI 분석은 Celery task로 이동했으므로 task import 추가
from .tasks import analyze_review_similarity_task


class EmbeddingAPIView(APIView):
    """
    [유지]
    Django -> FastAPI 임베딩 요청
    POST /ai/embed/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmbeddingRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        texts = serializer.validated_data["texts"]

        try:
            result = FastAPIClient.get_embeddings(texts)
            return Response(result, status=status.HTTP_200_OK)

        except RequestException as e:
            return Response(
                {"detail": f"FastAPI 호출 실패: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )


class SimilarityAPIView(APIView):
    """
    [유지]
    Django -> FastAPI 유사도 요청
    POST /ai/similarity/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SimilarityRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        text1 = serializer.validated_data["text1"]
        text2 = serializer.validated_data["text2"]

        try:
            result = FastAPIClient.get_similarity(text1, text2)
            return Response(result, status=status.HTTP_200_OK)

        except RequestException as e:
            return Response(
                {"detail": f"FastAPI 호출 실패: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )


# =========================================================
# [삭제]
# 기존 코드에는 View 안에서 직접 유사도 라벨을 만들기 위해
# get_similarity_label() 함수가 있었음
#
# 변경 후에는 실제 유사도 계산과 라벨 생성이 tasks.py 로 이동했으므로
# views.py 에서는 더 이상 이 함수가 필요 없어짐
# =========================================================
# def get_similarity_label(score: float) -> str:
#     if score > 0.7:
#         return "매우 비슷"
#     if score > 0.5:
#         return "비슷"
#     if score > 0.3:
#         return "약간 비슷"
#     return "관련 있음"


class ReviewAnalyzeAPIView(APIView):
    """
    [수정]
    기존:
    GET /ai/reviews/<review_id>/analyze/
    -> View 안에서 FastAPI 직접 호출
    -> DB 저장
    -> 결과 즉시 반환

    변경:
    POST /ai/reviews/<review_id>/analyze/
    -> Celery 작업만 등록
    -> task_id 반환
    """
    permission_classes = [AllowAny]

    # [수정]
    # 기존 코드에는 SIMILARITY_THRESHOLD, MODEL_NAME 상수가 클래스 내부에 있었음
    # 변경 후에는 실제 분석 로직이 tasks.py 로 이동했으므로 여기서는 제거됨

    def post(self, request, review_id):
        # [유지]
        # 기준 리뷰 존재 여부 먼저 확인
        source_review = get_object_or_404(
            Review.objects.select_related("user", "product"),
            id=review_id,
            is_public=True,
        )

        # [유지]
        # 기준 리뷰 내용이 비어 있으면 작업 등록 전 바로 에러 반환
        if not source_review.content.strip():
            return Response(
                {"detail": "분석할 리뷰 내용이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # [추가]
        # 로그인 사용자인 경우 요청자 ID 저장
        requested_by_id = request.user.id if request.user.is_authenticated else None

        # =========================================================
        # [추가]
        # 기존 코드에서는 여기서 직접 FastAPI 호출 + 결과 저장을 했음
        #
        # 변경 후에는 Celery task에게 실제 분석 작업을 맡김
        # -> delay() 호출 시 비동기 작업 등록
        # -> 즉시 task_id 반환 가능
        # =========================================================
        async_result = analyze_review_similarity_task.delay(
            review_id=source_review.id,
            requested_by_id=requested_by_id,
        )

        # =========================================================
        # [추가]
        # 기존 코드에는 없었음
        # 작업 시작 전 DB에 작업 상태를 먼저 저장
        # 나중에 상태 조회 API에서 이 레코드를 사용함
        # =========================================================
        AIAnalysisTask.objects.create(
            source_review=source_review,
            requested_by_id=requested_by_id,
            task_id=async_result.id,
            status=AIAnalysisTask.STATUS_PENDING,
            model_name="upskyy/e5-small-korean",
            similarity_threshold=0.45,
        )

        # =========================================================
        # [수정]
        # 기존:
        # 200 OK + 분석 결과(JSON) 즉시 반환
        #
        # 변경:
        # 202 ACCEPTED + task_id만 반환
        # 실제 결과는 나중에 상태 조회 API로 확인
        # =========================================================
        return Response(
            {
                "detail": "AI 분석 작업이 등록되었습니다.",
                "task_id": async_result.id,
                "status": "PENDING",
                "review_id": source_review.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ReviewAnalyzeTaskStatusAPIView(APIView):
    """
    [추가]
    Celery 작업 상태 조회 API
    GET /ai/tasks/<task_id>/status/

    역할:
    - 현재 작업 상태 확인
    - DB에 기록된 상태 확인
    - 작업 성공 시 최종 결과도 함께 반환
    """
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        # [추가]
        # DB에 저장된 작업 상태 레코드 조회
        task_obj = get_object_or_404(AIAnalysisTask, task_id=task_id)

        # [추가]
        # Celery 백엔드 기준 실제 task 상태 조회
        async_result = AsyncResult(task_id)

        # [추가]
        # 상태 조회용 기본 응답 데이터 구성
        response_data = {
            "task_id": task_id,
            "status": async_result.status,
            "db_status": task_obj.status,
            "error_message": task_obj.error_message,
            "candidate_count": task_obj.candidate_count,
            "result_count": task_obj.result_count,
            "created_at": task_obj.created_at,
            "started_at": task_obj.started_at,
            "finished_at": task_obj.finished_at,
        }

        # [추가]
        # 작업이 성공 완료된 경우 Celery task가 반환한 최종 결과 포함
        if async_result.successful():
            response_data["result"] = async_result.result

        return Response(response_data, status=status.HTTP_200_OK)