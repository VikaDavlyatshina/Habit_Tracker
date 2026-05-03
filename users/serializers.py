from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "avatar", "password"]

        read_only_fields = ["id"]

    def validate_email(self, value):
        """Проверяем, что email не занят"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return value

    def create(self, validated_data):
        """
        Создаёт пользователя с хэшированным паролем.
        """

        # Забираем пароль и email из словаря
        password = validated_data.pop("password")
        email = validated_data.pop("email")

        # Создаем пользователя
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования профиля."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "avatar"]
        read_only_fields = ["id", "email"]
