from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

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