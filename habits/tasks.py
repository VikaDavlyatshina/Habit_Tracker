from datetime import date, datetime

import pytz
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from habits.models import Habit


@shared_task
def check_and_send_reminders():
    """
    Каждую минуту находит привычки на текущее время и отправляет уведомления.
    """
    now = timezone.now()
    today = now.date()
    # Берём текущее время, убираем секунды (14:35:42 → 14:35:00)
    current_time = now.time().replace(second=0, microsecond=0)

    # Находим все привычки, у которых время совпадает с текущим
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
    )

    sent_count = 0

    for habit in habits:
        # Проверка 1: нужно ли отправлять сегодня (периодичность)
        if not _should_send_today(habit, today):
            continue
        # Проверка 2: привязан ли Telegram у пользователя
        if not habit.user.telegram_chat_id:
            continue

        # Обновляем дату последней отправки
        _send_telegram_message(habit.user.telegram_chat_id, _format_message(habit))

        habit.last_sent = today
        habit.save(update_fields=["last_sent"])
        sent_count += 1

    return f"Отправлено {sent_count} напоминаний"


def _should_send_today(habit, today):
    """
    Проверяет периодичность: нужно ли отправлять привычку сегодня.
    today — date (без времени).
    """
    # Если никогда не отправляли — отправляем в первый раз
    if not habit.last_sent:
        return True
    # Сколько дней прошло с последней отправки
    days_passed = (today - habit.last_sent).days
    # Отправляем, если прошло >= period дней
    return days_passed >= habit.period


def _format_message(habit):
    """Форматирует текст уведомления для Telegram."""
    emoji = "🎁" if habit.is_pleasant else "🎯"

    # Берём часовой пояс из настроек Django (Europe/Moscow)
    tz = pytz.timezone(settings.TIME_ZONE)

    # Берём время привычки (UTC), добавляем сегодняшнюю дату
    utc_time = datetime.combine(date.today(), habit.time)

    # Говорим Django: «Это время в UTC»
    utc_time = pytz.UTC.localize(utc_time)

    # Переводим в часовой пояс из настроек
    local_time = utc_time.astimezone(tz).strftime("%H:%M")

    text = (
        f"{emoji} Напоминание о привычке!\n\n"
        f"📍 Место: {habit.place}\n"
        f"⏰ Время: {local_time}\n"
        f"📋 Действие: {habit.action}\n"
        f"⏱ Длительность: {habit.duration // 60} мин."
    )

    if habit.reward:
        text += f"\n🏆 Награда: {habit.reward}"

    return text


def _send_telegram_message(chat_id, text):
    """Отправляет сообщение в Telegram через Bot API."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return  # Токен не настроен — выходим

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(
            url,
            data={"chat_id": chat_id, "text": text},
            timeout=10,  # Ждём не больше 10 секунд
        )
    except requests.RequestException:
        pass  # Ошибка сети или Telegram API — пропускаем, не ломаем задачу
