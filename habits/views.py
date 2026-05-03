from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets

from .models import Habit
from .paginators import HabitPagination
from .permissions import IsOwner
from .serializers import HabitSerializer, PublicHabitSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список моих привычек",
        description="Возвращает привычки текущего пользователя с пагинацией по 5 штук.",
        responses={200: HabitSerializer(many=True)},
        tags=["habits"],
    ),
    create=extend_schema(
        summary="Создать привычку",
        description="Создаёт новую привычку. Пользователь назначается автоматически.",
        request=HabitSerializer,
        responses={201: HabitSerializer},
        tags=["habits"],
    ),
    retrieve=extend_schema(
        summary="Просмотр привычки",
        tags=["habits"],
    ),
    update=extend_schema(
        summary="Обновить привычку",
        tags=["habits"],
    ),
    destroy=extend_schema(
        summary="Удалить привычку",
        tags=["habits"],
    ),
)
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


@extend_schema_view(
    get=extend_schema(
        summary="Публичный список привычек",
        description="Возвращает список привычек, у которых is_public=True. Доступно неавторизованным пользователям",
        request=PublicHabitSerializer,
        responses={200: PublicHabitSerializer(many=True)},
        tags=["habits"],
    )
)
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
        return Habit.objects.filter(is_public=True).order_by("-created_at")
