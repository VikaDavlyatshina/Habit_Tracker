from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Habit

User = get_user_model()


class HabitAPITestCase(TestCase):
    """Тесты для API привычек."""

    def setUp(self):
        """Создаём пользователя и получаем JWT-токен перед каждым тестом."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@test.com", password="StrongPassword123", first_name="Test"
        )
        response = self.client.post(
            "/api/users/login/",
            {"email": "testuser@test.com", "password": "StrongPassword123"},
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    # ── СОЗДАНИЕ ──

    def test_create_habit_success(self):
        """POST /api/habits/ → 201 Created."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)

    def test_create_habit_duration_0(self):
        """duration_minutes_input=0 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_duration_too_long(self):
        """duration_minutes_input=5 → 400 (максимум 2 минуты)."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 5,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_missing_fields(self):
        """POST без time, action, duration → 400."""

        response = self.client.post("/api/habits/", {"place": "Парк"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_period_7(self):
        """period=7 → 201 Created."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
                "period": 7,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_period_0(self):
        """period=0 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
                "period": 0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_period_8(self):
        """period=8 → 400 (максимум 7)."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
                "period": 8,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── БИЗНЕС-ЛОГИКА ──

    def test_cannot_have_both_related_habit_and_reward(self):
        """related_habit + reward одновременно → 400."""

        pleasant = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(20, 0),
            action="Принять ванну",
            is_pleasant=True,
            duration=60,
            period=1,
        )
        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
                "related_habit": pleasant.id,
                "reward": "Шоколадка",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_habit_must_be_pleasant(self):
        """Связанная привычка не приятная → 400."""

        useful = Habit.objects.create(
            user=self.user,
            place="Зал",
            time=time(9, 0),
            action="Силовая тренировка",
            is_pleasant=False,
            duration=120,
            period=1,
        )
        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
                "related_habit": useful.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_cannot_have_reward(self):
        """Приятная привычка + reward → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Дом",
                "time": "21:00",
                "action": "Чтение книги",
                "duration_minutes_input": 1,
                "is_pleasant": True,
                "reward": "Тортик",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_habit_must_be_own(self):
        """Чужая привычка как связанная → 400."""

        other_user = User.objects.create_user(
            email="foreign@test.com", password="ForeignPass123"
        )
        foreign = Habit.objects.create(
            user=other_user,
            place="Дом",
            time=time(20, 0),
            action="Чтение книги",
            is_pleasant=True,
            duration=60,
            period=1,
        )
        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 2,
                "related_habit": foreign.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── ПРАВА ДОСТУПА ──

    def test_cannot_edit_foreign_habit(self):
        """PUT чужой привычки → 404."""

        other = User.objects.create_user(
            email="other@test.com", password="OtherPass123"
        )
        habit = Habit.objects.create(
            user=other,
            place="Кафе",
            time=time(13, 0),
            action="Обеденный перерыв",
            duration=60,
            period=1,
        )
        response = self.client.put(
            f"/api/habits/{habit.id}/",
            {
                "place": "Офис",
                "time": "13:00",
                "action": "Обед",
                "duration_minutes_input": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_habit(self):
        """DELETE своей привычки → 204."""

        habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time=time(7, 0),
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.delete(f"/api/habits/{habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_retrieve_foreign_habit(self):
        """GET чужой привычки → 404."""

        other = User.objects.create_user(
            email="other2@test.com", password="OtherPass123"
        )
        habit = Habit.objects.create(
            user=other,
            place="Дом",
            time="08:00",
            action="Полноценный сон",
            duration=120,
            period=1,
        )
        response = self.client.get(f"/api/habits/{habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── ПРОСМОТР ──

    def test_list_my_habits(self):
        """GET /api/habits/ → только свои привычки."""

        Habit.objects.create(
            user=self.user,
            place="Парк",
            time=time(7, 0),
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.get("/api/habits/")
        self.assertEqual(response.data["count"], 1)

    def test_public_habits_visible_to_anonymous(self):
        """Публичные привычки видны без авторизации."""

        Habit.objects.create(
            user=self.user,
            place="Парк",
            time=time(7, 0),
            action="Утренняя пробежка",
            duration=120,
            is_public=True,
            period=1,
        )
        self.client.credentials()
        response = self.client.get("/api/habits/public/")
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_habit(self):
        """GET /api/habits/{id}/ → просмотр своей привычки."""

        habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time="07:00",
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.get(f"/api/habits/{habit.id}/")
        self.assertEqual(response.data["action"], "Утренняя пробежка")

    # ── ОБНОВЛЕНИЕ ──

    def test_update_habit_action_only(self):
        """PATCH только action → 200, действие обновлено."""

        habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time="07:00",
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.patch(
            f"/api/habits/{habit.id}/", {"action": "Вечерняя пробежка"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.action, "Вечерняя пробежка")

    def test_action_uniqueness_on_update(self):
        """PATCH с тем же action → 200 (без ошибки уникальности)."""

        habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time="07:00",
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.patch(
            f"/api/habits/{habit.id}/", {"action": "Утренняя пробежка"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_action_uniqueness_create_duplicate(self):
        """Повторное создание с тем же action → 400."""

        Habit.objects.create(
            user=self.user,
            place="Парк",
            time="07:00",
            action="Утренняя пробежка",
            duration=120,
            period=1,
        )
        response = self.client.post(
            "/api/habits/",
            {
                "place": "Зал",
                "time": "08:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── ВАЛИДАТОРЫ ──

    def test_validate_duration_below_1(self):
        """duration=0 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
                "duration": 0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_duration_above_120(self):
        """duration=121 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
                "duration": 121,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_period_below_1(self):
        """period=0 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
                "period": 0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_period_above_7(self):
        """period=8 → 400."""

        response = self.client.post(
            "/api/habits/",
            {
                "place": "Парк",
                "time": "07:00",
                "action": "Утренняя пробежка",
                "duration_minutes_input": 1,
                "period": 8,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
