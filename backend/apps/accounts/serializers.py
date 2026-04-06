from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    사용자 조회용 Serializer

    - 회원정보를 응답으로 보여줄 때 사용
    - 비밀번호는 절대 노출하지 않음
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class SignupSerializer(serializers.ModelSerializer):
    """
    회원가입용 Serializer

    - password, password_confirm 입력을 받음
    - 두 비밀번호가 일치하는지 검사
    - create_user()를 사용해서 비밀번호를 해시 저장
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=4,
        style={"input_type": "password"}
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        min_length=4,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate(self, attrs):
        """
        비밀번호 확인 검사
        """
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "비밀번호가 일치하지 않습니다."
            })

        return attrs

    def create(self, validated_data):
        """
        회원 생성

        - password_confirm 는 DB에 저장하지 않으므로 제거
        - create_user()를 사용해야 비밀번호가 해시 처리됨
        """
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user