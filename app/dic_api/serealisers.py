from rest_framework import serializers
from .models import DICAnalysis
import os


class DICAnalysisCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания задачи анализа."""
    
    class Meta:
        model = DICAnalysis
        fields = [
            'name',
            'image_before',
            'image_after',
            'subset_size',
            'step',
            'max_iter',
            'min_correlation'
        ]
    
    def validate_subset_size(self, value):
        if value % 2 == 0:
            value += 1  
        if value < 21:
            value = 21
        elif value > 31:
            value = 31
        return value


class DICAnalysisSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения задачи анализа."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # URL для изображений
    image_before_url = serializers.SerializerMethodField()
    image_after_url = serializers.SerializerMethodField()
    result_image_url = serializers.SerializerMethodField()
    original_image_url = serializers.SerializerMethodField()
    deformed_image_url = serializers.SerializerMethodField()
    displacement_map_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DICAnalysis
        fields = '__all__'
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 
            'started_at', 'completed_at', 'processing_time',
            'error_message', 'error_traceback', 'result_json',
            'mean_displacement', 'max_displacement', 'median_displacement',
            'std_displacement', 'correlation_quality', 'reliable_points_percentage',
            'result_image_path', 'original_image_path', 'deformed_image_path',
            'displacement_map_path'
        ]
    
    def get_image_before_url(self, obj):
        if obj.image_before:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_before.url)
        return None
    
    def get_image_after_url(self, obj):
        if obj.image_after:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_after.url)
        return None
    
    def get_result_image_url(self, obj):
        if obj.result_image_path and os.path.exists(obj.result_image_path):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/results/{os.path.basename(obj.result_image_path)}')
        return None
    
    def get_original_image_url(self, obj):
        if obj.original_image_path and os.path.exists(obj.original_image_path):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/results/{os.path.basename(obj.original_image_path)}')
        return None
    
    def get_deformed_image_url(self, obj):
        if obj.deformed_image_path and os.path.exists(obj.deformed_image_path):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/results/{os.path.basename(obj.deformed_image_path)}')
        return None
    
    def get_displacement_map_url(self, obj):
        if obj.displacement_map_path:
            from django.conf import settings
            full_path = os.path.join(settings.MEDIA_ROOT, obj.displacement_map_path)
            if os.path.exists(full_path):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(f'/media/results/{os.path.basename(obj.displacement_map_path)}')
        return None