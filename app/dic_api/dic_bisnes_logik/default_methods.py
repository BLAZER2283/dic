import logging
from rest_framework.response import Response
import os
from .help_methods import HelpMethods


logger = logging.getLogger(__name__)


class DefaultMethodsMixin:
    """Миксин с методами по умолчанию для DIC Analysis ViewSet."""

    def list(self, request, *args, **kwargs):
        """Получение списка всех задач с фильтрацией."""
        queryset = self.filter_queryset(self.get_queryset())

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        # Фильтрация по наличию результатов
        has_results = request.query_params.get("has_results")
        if has_results == "true":
            queryset = queryset.filter(results__displacement_map_path__isnull=False)
        elif has_results == "false":
            queryset = queryset.filter(results__displacement_map_path__isnull=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Получение деталей задачи с абсолютными URL."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
