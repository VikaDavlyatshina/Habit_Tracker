from django.core.exceptions import ValidationError

def validate_duration(value):
    """
    Проверяет время выполнения привычки.
    value — число секунд, которое передал пользователь.
    """
    if value < 1:
        raise ValidationError('Время выполнения должно быть больше 0')
    if value > 120:
        raise ValidationError(
            f'Слишком долго! Максимум 120 секунд (2 минуты). Вы указали: {value}'
        )


def validate_period(value):
    """
    Проверяет периодичность привычки.
    value — число дней, которое передал пользователь.
    """
    if value < 1:
        raise ValidationError('Период не может быть меньше 1 дня')
    if value > 7:
        raise ValidationError(
            f'Период не может быть больше 7 дней. Вы указали: {value}'
        )