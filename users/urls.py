from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import LinkTelegramView

app_name = UsersConfig.name

urlpatterns = [
    # Авторизация (JWT)
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Telegram
    path('telegram/link/', LinkTelegramView.as_view(), name='link-telegram'),
]