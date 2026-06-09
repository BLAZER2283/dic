from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import Authenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import AnalysisTask, 
from .serealisers import (
    AnalysisTaskSerializer,
    AnalysisTaskCreateSerializer,
)
from .dic_bisnes_logik.default_methods import DefaultMethodsMixin
from .dic_bisnes_logik.logik_image import ImageActionsMixin
from .dic_bisnes_logik.generate import PdfGenerateMixin


class AnalysisTaskViewSet(
    DefaultMethodsMixin,
    ImageActionsMixin,
    PdfGenerateMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet для работы с задачами DIC анализа.
    """

    queryset = AnalysisTask.objects.all().select_related(
        'sample', 'parameters', 'images', 'results'
    ).order_by('-created_at')
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [Authenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalysisTaskCreateSerializer
        return AnalysisTaskSerializer

    def create(self, request, *args, **kwargs):
        """Создание новой задачи анализа."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        response_serializer = AnalysisTaskSerializer(
            task, context={"request": request}
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
