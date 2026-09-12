# Habit Tracker

Трекер полезных привычек с Telegram-уведомлениями. Backend на Django REST Framework.

## Описание

API для трекера полезных привычек. Пользователи создают привычки, получают напоминания в Telegram по расписанию. 
Реализована JWT-авторизация, пагинация, документация Swagger.


## Стек

- Python 3.13, Django 6.0, DRF
- PostgreSQL 17, Redis 7
- Celery + Celery Beat
- JWT (Simple JWT)
- Telegram Bot API
- Docker + Docker Compose
- Gunicorn

## Установка и запуск

### Требования

- Python 3.13+
- Poetry
- PostgreSQL
- Redis

### Установка

#### 1. Клонируйте репозиторий:

- Ссылка на репозиторий: https://github.com/VikaDavlyatshina/Habit_Tracker

```bash
git clone https://github.com/VikaDavlyatshina/Habit_Tracker HabitTracker
```

#### 2. Перейдите в папку проекта

```bash
cd HabitTracker
```

#### 3. Установите зависимости

```bash
poetry install
```

#### 4. Настройте переменные окружения

 Отредактируйте .env — укажите свои данные (токен бота, параметры БД).

```bash
cp .env.template .env
```

#### 5. Примените миграции

```bash
python manage.py migrate
```
### Запуск

- **Запустите сервер**:

```bash
python manage.py runserver
```

- **Запустите Celery Worker (в отдельном терминале)**:

```bash
celery -A config worker -l info -P eventlet
```

- **Запустите Celery Beat (в отдельном терминале)**:

```bash
celery -A config beat -l info
```

## Запуск через Docker

1. Убедитесь, что Docker Desktop запущен

2. Создайте файл с настройками:
```bash
cp .env.template .env
```
3. Запустите все сервисы:

```bash
docker compose up -d --build
```
4. Откройте сайт: http://localhost:8080


## Доступ

- Админка: [http://89.169.174.52:8080/admin/](http://89.169.174.52:8080/admin/)
- API: [http://89.169.174.52:8080/api/habits/](http://89.169.174.52:8080/api/habits/)
- Swagger: [http://89.169.174.52:8080/api/docs/](http://89.169.174.52:8080/api/docs/)

## API

**Регистрация и авторизация:**
- `POST /api/users/register/` — регистрация (доступ всем)
- `POST /api/users/login/` — получить JWT-токены (доступ всем)
- `POST /api/users/token/refresh/` — обновить access-токен (доступ всем)

**Профиль:**
- `GET/PUT/DELETE /api/users/profile/` — свой профиль (только авторизованным)
- `POST /api/users/telegram/link/` — привязать Telegram (только авторизованным)

**Привычки:**
- `GET /api/habits/` — список своих привычек (авторизованным)
- `POST /api/habits/` — создать привычку (авторизованным)
- `GET/PUT/DELETE /api/habits/{id}/` — просмотр/обновить/удалить (авторизованным)
- `GET /api/habits/public/` — публичные привычки (доступ всем)


## Документация

- Swagger (локально): http://localhost:8000/api/docs/
- Swagger (Docker): http://localhost:8080/api/docs/
- Redoc: http://localhost:8000/api/redoc/
- Redoc (Docker): http://localhost:8080/api/redoc/

## Тесты

```bash
python manage.py test
```

Покрытие: 85%+ (отчёт: coverage_report.txt)


## Проверка работы

### Статус контейнеров (Docker)

```bash
docker compose ps
```

Все сервисы должны быть в статусе Up.

### Redis (Docker)

```bash
docker compose exec redis redis-cli PING
```

Ожидаемый ответ: PONG

## CI/CD

#### Проект автоматически деплоится на сервер при каждом `push` в репозиторий через GitHub Actions. 

**Пайплайн включает:**

 - Линтинг (Flake8)

 - Тесты

 - Сборку Docker-образа

 - Публикацию в Docker Hub

 - Деплой на сервер

## 👤 Автор

Виктория Давлятшина