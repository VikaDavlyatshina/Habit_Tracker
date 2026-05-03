from rest_framework import viewsets, generics, permissions
from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer
from .permissions import IsOwner
from .paginators import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операций с привычками пользователя.

    Автоматически создаёт эндпоинты:
    - GET /habits/ — список привычек пользователя
    - POST /habits/ — создать новую привычку
    - GET /habits/{id}/ — посмотреть одну привычку
    - PUT /habits/{id}/ — полностью обновить привычку
    - PATCH /habits/{id}/ — частично обновить привычку
    - DELETE /habits/{id}/ — удалить привычку

    Для работы с router, который создаст URL автоматически.
    """

    # Какой сериализатор использовать для отображения
    serializer_class = HabitSerializer

    # Кто может выполнять действия
    # IsAuthenticated — только авторизованные пользователи
    # IsOwner — только владелец привычки (для просмотра/обновления/удаления)
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    # Пагинация (5 привычек на страницу)
    pagination_class = HabitPagination

    def get_queryset(self):
        """
        Какие привычки показывать.

        Возвращает привычки текущего пользователя.
        """

        # Если пользователь не авторизован — пустой список
        if not self.request.user.is_authenticated:
            return Habit.objects.none()

        # Только привычки текущего пользователя
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает привычку к текущему пользователю.
        """

        # serializer.save() сохраняет объект в базу
        # user=self.request.user — привязываем к тому, кто делает запрос
        serializer.save(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """
    Публичный список привычек.

    Доступен ВСЕМ (даже без авторизации).
    Показывает только привычки, у которых is_public=True.
    """

    # Сериализатор для публичного списка (без поля user)
    serializer_class = PublicHabitSerializer

    permission_classes = [permissions.AllowAny]

    pagination_class = HabitPagination

    def get_queryset(self):
        """
        Какие привычки показывать в публичном списке.

        Возвращает только те, у которых is_public=True.
        Сортируем по дате создания — сначала новые.
        """
        return Habit.objects.filter(is_public=True).order_by('-created_at')
