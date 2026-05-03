from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import HabitsConfig
from .views import HabitViewSet, PublicHabitListView


app_name = HabitsConfig.name
# ============================================
# ROUTER — автоматически создаёт URL для ViewSet
# ============================================
router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

# После регистрации router создаст такие URL:
# GET    /habits/        → список
# POST   /habits/        → создать
# GET    /habits/{id}/   → просмотр
# PUT    /habits/{id}/   → обновить
# PATCH  /habits/{id}/   → частично обновить
# DELETE /habits/{id}/   → удалить

urlpatterns = [
    # Публичные привычки (отдельный эндпоинт)
    path('habits/public/', PublicHabitListView.as_view(), name='public-habits'),
    # Все URL от router (CRUD для привычек)
    path('', include(router.urls)),
]