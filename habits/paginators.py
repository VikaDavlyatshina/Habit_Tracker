from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Пагинация для привычек.

    Параметры:
    - page_size — сколько объектов на одной странице
    - page_size_query_param — параметр для изменения размера страницы
    - max_page_size — но не больше 50
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50