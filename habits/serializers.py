from rest_framework import serializers

from .models import Habit
from .validators import validate_duration, validate_period


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit.
    """

    # === ПОЛЯ ДЛЯ КОНВЕРТАЦИИ МИНУТЫ <-> СЕКУНДЫ ===

    # Только для чтения (GET): возвращает минуты из секунд
    duration_minutes = serializers.SerializerMethodField(read_only=True)

    # Только для записи (POST/PUT): принимает минуты от пользователя
    # Ограничение: 1-2 минуты
    duration_minutes_input = serializers.IntegerField(
        write_only=True,
        min_value=1,
        max_value=2,
        help_text="Время выполнения привычки в минутах (1 или 2)",
    )

    # Внутреннее поле: хранит секунды в БД
    # Пользователь его не видит, но оно нужно для валидации
    duration = serializers.IntegerField(
        write_only=True,
        required=False,  # Необязательно, т.к. есть duration_minutes_input
        validators=[validate_duration],
    )

    # === АВТОМАТИЧЕСКИЕ ПОЛЯ ===

    # Пользователь подставляется из текущего запроса (не нужно передавать в теле)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Периодичность: по умолчанию 1 раз в день
    period = serializers.IntegerField(
        validators=[validate_period], required=False, default=1
    )

    class Meta:
        model = Habit
        fields = [
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "period",
            "reward",
            "duration",
            "is_public",
            "user",
            "created_at",
            "updated_at",
            "duration_minutes",
            "duration_minutes_input",
        ]
        read_only_fields = ["created_at", "updated_at"]  # Автополя не редактируются

    # === МЕТОДЫ ДЛЯ КОНВЕРТАЦИИ ===

    def get_duration_minutes(self, obj):
        """
        Преобразует секунды в минуты для ответа API.

        Пример: obj.duration = 120 → возвращает 2
        """
        return obj.duration // 60

    # === ВАЛИДАТОРЫ ПОЛЕЙ ===

    def validate_place(self, value):
        """
        Проверка места выполнения привычки.

        Требование: минимум 3 символа (пробелы в начале/конце не считаются)
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название места должно содержать хотя бы 3 символа"
            )
        return value

    def validate_action(self, value):
        """
        Проверка названия действия.

        Условия:
        1. Минимум 5 символов
        2. Уникальность в рамках одного пользователя (без учета регистра)
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Опишите действие подробнее (минимум 5 символов)"
            )

        # Проверка уникальности (без учета регистра)
        user = self.context["request"].user
        queryset = Habit.objects.filter(user=user, action__iexact=value.strip())

        # При обновлении исключаем текущую привычку из проверки
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "У вас уже есть привычка с таким действием"
            )

        return value

    # === КОМПЛЕКСНАЯ ВАЛИДАЦИЯ (связи между полями) ===

    def validate(self, data):
        """
        Валидация, требующая проверки нескольких полей одновременно.

        Логика:
        1. Конвертация минут в секунды
        2. Проверка обязательных полей при создании
        3. Валидация правил для приятных привычек
        4. Валидация связей между полями
        """
        request = self.context.get("request")
        is_create = request and request.method == "POST"

        # 1) Конвертация минут → секунды

        # Если пользователь передал минуты, преобразуем их в секунды для БД
        if "duration_minutes_input" in data:
            data["duration"] = data.pop("duration_minutes_input") * 60

        #  2) Проверка обязательных полей при создании

        # При создании привычки duration обязателен
        if is_create and "duration" not in data:
            raise serializers.ValidationError({"duration": "Укажите время выполнения"})

        # При создании: место, время и действие обязательны
        if is_create:
            required = ["place", "time", "action"]
            for field in required:
                if not data.get(field):
                    raise serializers.ValidationError(
                        {field: f'Поле "{field}" обязательно'}
                    )

        # 3) Правила для приятных привычек
        # Приятная привычка не может иметь награду
        if data.get("is_pleasant") and data.get("reward"):
            raise serializers.ValidationError(
                {"reward": "У приятной привычки не может быть вознаграждения"}
            )

        # Приятная привычка не может иметь связанную привычку
        if data.get("is_pleasant") and data.get("related_habit"):
            raise serializers.ValidationError(
                {
                    "related_habit": "У приятной привычки не может быть связанной привычки"
                }
            )

        # 4) Проверка взаимоисключающих полей
        # Нельзя выбрать одновременно "связанную привычку" и "вознаграждение"
        if data.get("related_habit") and data.get("reward"):
            raise serializers.ValidationError(
                {
                    "related_habit": "Нельзя выбрать одновременно связанную привычку и вознаграждение",
                    "reward": "Нельзя выбрать одновременно связанную привычку и вознаграждение",
                }
            )

        # 5) Правила для связанной привычки
        if data.get("related_habit"):
            # Связанная привычка должна быть приятной
            if not data["related_habit"].is_pleasant:
                raise serializers.ValidationError(
                    {"related_habit": "Связанная привычка должна быть приятной"}
                )

            # Можно выбирать только свои привычки
            user = request.user if request else None
            if user and data["related_habit"].user != user:
                raise serializers.ValidationError(
                    {"related_habit": "Можно выбирать только свои привычки"}
                )

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичного списка привычек.

    Отличия от основного:
    - Только чтение
    - Показывает только разрешенные поля
    - Скрывает личную информацию (вознаграждение, связанные привычки)
    """

    duration_minutes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Habit
        # Публичный список: только основные поля
        fields = [
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "period",
            "duration_minutes",
        ]

    def get_duration_minutes(self, obj):
        """Преобразует секунды в минуты для публичного API"""
        return obj.duration // 60
