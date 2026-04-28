# Habit Tracker

Трекер полезных привычек с Telegram-уведомлениями. Backend на Django REST Framework.

## Стек

- **Python** 3.13
- **Django** 6.0 + **DRF**
- **PostgreSQL** 17
- **Redis** 7 + **Celery**
- **JWT** (Simple JWT)
- **Telegram Bot API**
- **Docker** + **Docker Compose**

## Установка

### Локально

```bash
git clone https://github.com/VikaDavlyatshina/Habit_Tracker
cd HabitTracker
poetry install
cp .env.example .env  # заполнить своими данными
python manage.py migrate
python manage.py runserver
```