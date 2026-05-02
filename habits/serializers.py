from rest_framework import serializers
from datetime import time
from .models import Habit
from .validators import validate_duration, validate_period


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек."""

    # Только для отображения (GET) — показывает минуты пользователю
    duration_minutes = serializers.SerializerMethodField(read_only=True)

    # Только для ввода (POST/PUT) — пользователь передаёт минуты
    duration_minutes_input = serializers.IntegerField(
        write_only=True,
        min_value=1,
        max_value=2,
        help_text='Время в минутах (1 или 2)'
    )

    # Секунды — только для внутреннего использования
    duration = serializers.IntegerField(
        write_only=True,
        required=False,  # Не обязательно, если передали duration_minutes_input
        validators=[validate_duration]
    )

    # Пользователь подставляется автоматически
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    period = serializers.IntegerField(validators=[validate_period])

    class Meta:
        model = Habit
        fields = [
            'id', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'period', 'reward', 'duration',
            'is_public', 'user', 'created_at', 'updated_at',
            'duration_minutes', 'duration_minutes_input'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_duration_minutes(self, obj):
        """ Переводит секунды в минуты для ответа """
        return obj.duration // 60

    def validate_place(self, value):
        """ Место - минимум 3 символа """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                'Название места должно содержать хотя бы 3 символа'
            )
        return value

    def validate_action(self, value):
        """ Дествие - минимум 5 символов """
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Опишите действие подробнее (минимум 5 символов)'
            )

        user = self.context['request'].user
        queryset = Habit.objects.filter(user=user, action__iexact=value.strip())

        # При обновлении исключаем текущую привычку
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                'У вас уже есть привычка с таким действием'
            )

        return value

    def validate_time(self, value):
        """Время: между 05:00 и 23:59."""

        if value < time(5, 0) or value > time(23, 59):
            raise serializers.ValidationError(
                'Время должно быть между 05:00 и 23:59'
            )
        return value

    def validate(self, data):
        """Проверка всех полей."""

        # Перевод минут в секунды
        if 'duration_minutes_input' in data:
            data['duration'] = data.pop('duration_minutes_input') * 60

        # Проверка, что duration передан
        if 'duration' not in data:
            raise serializers.ValidationError({
                'duration': 'Укажите время выполнения'
            })

        # Нельзя редактировать чужую привычку
        request = self.context.get('request')
        if self.instance and request and self.instance.user != request.user:
            raise serializers.ValidationError(
                'Вы не можете редактировать чужую привычку'
            )

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного списка."""

    duration_minutes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'place', 'time', 'action', 'is_pleasant', 'period', 'duration_minutes']

    def get_duration_minutes(self, obj):
        return obj.duration // 60