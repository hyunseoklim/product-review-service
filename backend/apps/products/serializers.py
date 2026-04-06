from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # =========================================================
    # [추가]
    # 이미지 업로드를 serializer에서 명시적으로 받기 위한 필드
    # - required=False : 이미지 없이도 생성/수정 가능
    # - allow_null=True : null 허용
    # Product 모델에 image 필드가 있는 구조에 맞춘 부분
    # =========================================================
    image = serializers.ImageField(required=False, allow_null=True)

    # =========================================================
    # [추가]
    # 프론트엔드에서 바로 사용할 수 있는 이미지 URL을 내려주기 위한 필드
    # DB에 저장된 image 자체와 별도로 image_url 값을 응답에 포함합니다.
    # =========================================================
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",

            # =================================================
            # [추가/유지]
            # Product 모델의 이미지 필드
            # =================================================
            "image",

            # =================================================
            # [추가]
            # 클라이언트에서 미리보기/출력용으로 사용하는 URL 필드
            # =================================================
            "image_url",

            "created_at",
        ]

    # =========================================================
    # [추가]
    # image 필드의 실제 접근 가능한 URL을 만들어 반환하는 메서드
    #
    # 예:
    # - request가 있으면 절대경로:
    #   http://127.0.0.1:8000/media/products/a.jpg
    #
    # - request가 없으면 상대경로:
    #   /media/products/a.jpg
    # =========================================================
    def get_image_url(self, obj):
        request = self.context.get("request")

        # [추가]
        # 이미지가 없으면 None 반환
        if not obj.image:
            return None

        try:
            image_url = obj.image.url
        except Exception:
            # [추가]
            # 파일 접근 중 예외가 나면 안전하게 None 반환
            return None

        # [추가]
        # request가 있으면 절대 URL 생성
        if request:
            return request.build_absolute_uri(image_url)

        # [추가]
        # request가 없으면 상대 URL 반환
        return image_url