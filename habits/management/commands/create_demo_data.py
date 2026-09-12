from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from habits.models import Habit

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт демо-данные: двух пользователей и привычки для них"

    def handle(self, *args, **options):
        # Создаём пользователей
        alice, _ = User.objects.get_or_create(
            email="alice@test.com",
            defaults={
                "first_name": "Алиса",
                "password": "alice12345",
                "telegram_chat_id": 111111111,
            },
        )
        alice.set_password("alice12345")
        alice.save()

        bob, _ = User.objects.get_or_create(
            email="bob@test.com",
            defaults={
                "first_name": "Боб",
                "password": "bob12345",
                "telegram_chat_id": 222222222,
            },
        )
        bob.set_password("bob12345")
        bob.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Пользователи созданы: alice@test.com, bob@test.com (пароль = имя + 12345)"
            )
        )

        # Привычки Алисы
        Habit.objects.get_or_create(
            user=alice,
            place="Парк Горького",
            time=time(7, 0),
            defaults={
                "action": "Утренняя пробежка",
                "is_public": True,
                "reward": "Протеиновый батончик",
                "duration": 120,
                "period": 1,
            },
        )
        Habit.objects.get_or_create(
            user=alice,
            place="Дом",
            time=time(21, 0),
            defaults={
                "action": "Принять тёплую ванну",
                "is_pleasant": True,
                "duration": 120,
                "period": 2,
            },
        )
        Habit.objects.get_or_create(
            user=alice,
            place="Кухня",
            time=time(8, 0),
            defaults={"action": "Выпить стакан воды", "duration": 30, "period": 1},
        )
        Habit.objects.get_or_create(
            user=alice,
            place="Спальня",
            time=time(22, 0),
            defaults={
                "action": "Чтение книги перед сном",
                "is_public": True,
                "reward": "Вкусный чай",
                "duration": 120,
                "period": 1,
            },
        )
        Habit.objects.get_or_create(
            user=alice,
            place="Балкон",
            time=time(6, 30),
            defaults={"action": "Утренняя растяжка", "duration": 120, "period": 1},
        )

        # Привычки Боба
        Habit.objects.get_or_create(
            user=bob,
            place="Спортзал",
            time=time(18, 0),
            defaults={
                "action": "Силовая тренировка",
                "is_public": True,
                "duration": 120,
                "period": 2,
            },
        )
        Habit.objects.get_or_create(
            user=bob,
            place="Дом",
            time=time(20, 0),
            defaults={
                "action": "Просмотр сериала",
                "is_pleasant": True,
                "duration": 120,
                "period": 1,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Привычки созданы: {Habit.objects.filter(user=alice).count()} у Алисы, "
                f"{Habit.objects.filter(user=bob).count()} у Боба"
            )
        )
