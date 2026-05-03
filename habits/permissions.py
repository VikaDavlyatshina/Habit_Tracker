from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем привычки.

    Как работает:
    -  has_permission() — не переопределён.
       Наследуется от BasePermission и возвращает True (доступ разрешён на уровне списка).

    - has_object_permission() — вызывается автоматически для одного объекта (просмотр, обновление, удаление)
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверка для конкретного объекта.
        obj — это привычка, которую пользователь пытается изменить.
        """
        # Возвращаем True, если пользователь — владелец привычки
        return obj.user == request.user