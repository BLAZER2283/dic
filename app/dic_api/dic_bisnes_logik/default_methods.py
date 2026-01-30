import threading  
from ..serealisers import DICAnalysisSerializer
from rest_framework.response import Response
import os
from rest_framework import status
from rest_framework import viewsets
from .help_methods import HelpMethods

class DefaultMethodsMixin(viewsets.ModelViewSet):
    
    def create(self, request, *args, **kwargs):
        """Создание новой задачи анализа."""
        print(f"DEBUG: Create request data keys: {list(request.data.keys())}")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request content type: {request.content_type}")

        serializer = self.get_serializer(data=request.data)
        print(f"DEBUG: Serializer is valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        
        dic_analysis = serializer.save()
        
        task_id = str(dic_analysis.id)
        
        thread = threading.Thread(
            target=HelpMethods()._process_dic_task,
            args=(
                task_id,
                dic_analysis.image_before.path,
                dic_analysis.image_after.path,
                dic_analysis.subset_size,
                dic_analysis.step,
                dic_analysis.max_iter,
                dic_analysis.min_correlation
            ),
            daemon=True
        )
        thread.start()
        
        response_serializer = DICAnalysisSerializer(
            dic_analysis,
            context={'request': request}
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def list(self, request, *args, **kwargs):
        """Получение списка всех задач с фильтрацией."""
        queryset = self.filter_queryset(self.get_queryset())
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        has_results = request.query_params.get('has_results')
        if has_results == 'true':
            queryset = queryset.filter(displacement_map_path__isnull=False)
        elif has_results == 'false':
            queryset = queryset.filter(displacement_map_path__isnull=True)
        
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
        data = serializer.data
        
        if instance.displacement_map_path:
            from django.conf import settings
            full_path = os.path.join(settings.MEDIA_ROOT, instance.displacement_map_path)
            if os.path.exists(full_path):
                data['displacement_map_url'] = request.build_absolute_uri(
                    f'/media/results/{os.path.basename(instance.displacement_map_path)}'
                )
        
        if instance.image_before:
            data['image_before_url'] = request.build_absolute_uri(
                instance.image_before.url
            )
        
        if instance.image_after:
            data['image_after_url'] = request.build_absolute_uri(
                instance.image_after.url
            )
        
        return Response(data)
    
    