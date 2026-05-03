from django.shortcuts import render
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserCreateSerializer


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

