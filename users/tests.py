from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserAPITestCase(TestCase):
    """Тесты для API пользователей."""

    def setUp(self):
        """Создаём клиент API перед каждым тестом."""
        self.client = APIClient()

    def test_register_user(self):
        """Регистрация нового пользователя (201 Created)."""
        response = self.client.post(
            "/api/users/register/",
            {"email": "newuser@test.com", "password": "NewUserPass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_existing_email(self):
        """Нельзя зарегистрироваться с уже занятым email (400)."""
        User.objects.create_user(email="test@test.com", password="pass123")
        response = self.client.post(
            "/api/users/register/",
            {"email": "test@test.com", "password": "SomePass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_jwt_token(self):
        """Успешное получение JWT-токена (200 OK, есть access)."""
        User.objects.create_user(email="test@test.com", password="pass123")
        response = self.client.post(
            "/api/users/login/", {"email": "test@test.com", "password": "pass123"}
        )
        self.assertIn("access", response.data)

    def test_login_wrong_password(self):
        """Ошибка 401 при входе с неверным паролем."""
        User.objects.create_user(email="test@test.com", password="pass123")
        response = self.client.post(
            "/api/users/login/", {"email": "test@test.com", "password": "wrong"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Обновление access-токена через refresh-токен."""
        # Создаём пользователя и получаем токены
        User.objects.create_user(email="test@test.com", password="pass123")
        login_response = self.client.post(
            "/api/users/login/", {"email": "test@test.com", "password": "pass123"}
        )
        # Извлекаем refresh-токен из ответа
        refresh = login_response.data["refresh"]
        # Обновляем access-токен
        response = self.client.post("/api/users/token/refresh/", {"refresh": refresh})
        self.assertIn("access", response.data)

    def test_get_my_profile(self):
        """Просмотр своего профиля (200 OK)."""
        user = User.objects.create_user(email="test@test.com", password="pass123")
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_my_profile(self):
        """Обновление своего профиля (200 OK, имя изменилось)."""
        user = User.objects.create_user(email="test@test.com", password="pass123")
        self.client.force_authenticate(user=user)
        response = self.client.patch("/api/users/profile/", {"first_name": "Новое"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_my_profile(self):
        """Удаление своего профиля (204 No Content)."""
        user = User.objects.create_user(email="test@test.com", password="pass123")
        self.client.force_authenticate(user=user)
        response = self.client.delete("/api/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
