from django.shortcuts import render
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserCreateSerializer, UserSerializer


# Create your views here.

@extend_schema(
    summary="Привязать Telegram",
    description="Сохраняет chat_id пользователя для отправки уведомлений о привычках.",
    tags=["users"],
)
class LinkTelegramView(APIView):
    """ Привязка Телеграм """

    def post(self, request):
        chat_id = request.data.get('telegram_chat_id')
        if not chat_id:
            return Response({'error': 'Не указан telegram_chat_id'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.telegram_chat_id = chat_id
        request.user.save()

        return Response({
            'status': 'updated',
            'telegram_chat_id': chat_id
        })

@extend_schema_view(
    post=extend_schema(
        summary="Регистрация пользователя. Доступна всем",
        description="Создаёт нового пользователя",
        request=UserCreateSerializer,
        responses={201: UserCreateSerializer, 400: None},
        tags=["users"],
    )
)
class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя (доступна всем)"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    # Разрешаем регистрацию всем
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    get=extend_schema(summary="Мой профиль", tags=["users"]),
    put=extend_schema(summary="Обновить профиль", tags=["users"]),
    patch=extend_schema(summary="Частично обновить профиль", tags=["users"]),
    delete=extend_schema(summary="Удалить профиль", tags=["users"]),
)
class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """ Просмотр, редактирование и удаление своего профиля """

    serializer_class = UserSerializer

    def get_object(self):
        # Получаем свой профиль
        return self.request.user