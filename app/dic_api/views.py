from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import AnalysisTask, Sample
from .serealisers import (
    AnalysisTaskSerializer,
    AnalysisTaskCreateSerializer,
    SampleSerializer,
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
    permission_classes = [AllowAny]
    filterset_fields = ['status', 'sample__material']
    search_fields = ['name', 'id', 'sample__name']
    ordering_fields = ['created_at', 'completed_at', 'processing_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalysisTaskCreateSerializer
        return AnalysisTaskSerializer

    def create(self, request, *args, **kwargs):
        """Создание новой задачи анализа."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        # Запускаем обработку в отдельном потоке
        from .dic_bisnes_logik.help_methods import HelpMethods
        import threading

        images = task.images
        parameters = task.parameters

        thread = threading.Thread(
            target=HelpMethods()._process_dic_task,
            args=(
                str(task.id),
                images.image_before.path,
                images.image_after.path,
                parameters.subset_size,
                parameters.step,
                parameters.max_iter,
                parameters.min_correlation,
            ),
            daemon=True,
        )
        thread.start()

        response_serializer = AnalysisTaskSerializer(
            task, context={"request": request}
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
