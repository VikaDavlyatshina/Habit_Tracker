from django.contrib import admin

from habits.models import Habit

# Register your models here.


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Админка для управления привычками."""

    # Какие поля показывать в списке
    list_display = [
        "id",
        "user",
        "place",
        "time",
        "action",
        "is_pleasant",
        "period",
        "is_public",
    ]

    # По каким полям можно искать
    search_fields = ["place", "action"]

    # Фильтры справа
    list_filter = ["is_pleasant", "is_public", "period"]

    # Поля только для чтения
    readonly_fields = ["created_at", "updated_at"]
