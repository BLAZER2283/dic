from rest_framework import serializers
from .models import Sample, AnalysisTask, AnalysisParameters, AnalysisImages, AnalysisResults
import os



class SampleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели образца."""

    class Meta:
        model = Sample
        fields = [
            'id', 'name', 'material', 'manufacture',
            'test_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']



class AnalysisParametersSerializer(serializers.ModelSerializer):
    """Сериализатор для параметров анализа."""

    class Meta:
        model = AnalysisParameters
        fields = [
            'id', 'subset_size', 'step', 'max_iter',
            'min_correlation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_subset_size(self, value):
        # Округляем до нечётного
        if value % 2 == 0:
            value += 1
        # Ограничиваем диапазон
        if value < 21:
            value = 21
        elif value > 31:
            value = 31
        return value



class AnalysisImagesSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений."""

    image_before_url = serializers.SerializerMethodField()
    image_after_url = serializers.SerializerMethodField()
    result_image_url = serializers.SerializerMethodField()
    original_image_url = serializers.SerializerMethodField()
    deformed_image_url = serializers.SerializerMethodField()
    displacement_map_url = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisImages
        fields = [
            'id', 'image_before', 'image_after',
            'result_image_path', 'original_image_path',
            'deformed_image_path', 'displacement_map_path',
            'image_before_url', 'image_after_url',
            'result_image_url', 'original_image_url',
            'deformed_image_url', 'displacement_map_url'
        ]
        read_only_fields = ['id']

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



class AnalysisResultsSerializer(serializers.ModelSerializer):
    """Сериализатор для результатов анализа."""

    class Meta:
        model = AnalysisResults
        fields = [
            'id', 'result_json', 'mean_displacement',
            'max_displacement', 'median_displacement',
            'std_displacement', 'correlation_quality',
            'reliable_points_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']



class AnalysisTaskCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания задачи анализа."""

    # Поля образца (запись только в БД)
    sample_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    material = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    manufacture = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    test_date = serializers.DateField(write_only=True, required=False, allow_null=True)

    # Поля параметров
    subset_size = serializers.IntegerField(write_only=True, default=25)
    step = serializers.IntegerField(write_only=True, default=12)
    max_iter = serializers.IntegerField(write_only=True, default=35)
    min_correlation = serializers.FloatField(write_only=True, default=0.4)

    # Изображения
    image_before = serializers.ImageField(write_only=True)
    image_after = serializers.ImageField(write_only=True)

    class Meta:
        model = AnalysisTask
        fields = [
            'id', 'name', 'status',
            'sample_name', 'material', 'manufacture', 'test_date',
            'subset_size', 'step', 'max_iter', 'min_correlation',
            'image_before', 'image_after',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Извлекаем данные для Sample
        sample_data = {
            'name': validated_data.pop('sample_name', 'Образец'),
            'material': validated_data.pop('material', None),
            'manufacture': validated_data.pop('manufacture', None),
            'test_date': validated_data.pop('test_date', None),
        }
        sample = Sample.objects.create(**sample_data)

        # Извлекаем данные для параметров
        params_data = {
            'subset_size': validated_data.pop('subset_size', 25),
            'step': validated_data.pop('step', 12),
            'max_iter': validated_data.pop('max_iter', 35),
            'min_correlation': validated_data.pop('min_correlation', 0.4),
        }

        # Извлекаем изображения
        images_data = {
            'image_before': validated_data.pop('image_before'),
            'image_after': validated_data.pop('image_after'),
        }

        # Создаём задачу
        task = AnalysisTask.objects.create(sample=sample, **validated_data)

        # Создаём связанные объекты
        AnalysisParameters.objects.create(task=task, **params_data)
        AnalysisImages.objects.create(task=task, **images_data)
        AnalysisResults.objects.create(task=task)

        return task


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения задачи анализа."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Плоские поля образца для совместимости с фронтендом
    sample_name = serializers.CharField(source='sample.name', read_only=True)
    material = serializers.CharField(source='sample.material', read_only=True, allow_null=True)
    manufacturer = serializers.CharField(source='sample.manufacture', read_only=True, allow_null=True)
    test_date = serializers.DateField(source='sample.test_date', read_only=True, allow_null=True)
    
    # Плоские поля параметров для удобства
    subset_size = serializers.IntegerField(source='parameters.subset_size', read_only=True, allow_null=True)
    step = serializers.IntegerField(source='parameters.step', read_only=True, allow_null=True)
    max_iter = serializers.IntegerField(source='parameters.max_iter', read_only=True, allow_null=True)
    min_correlation = serializers.FloatField(source='parameters.min_correlation', read_only=True, allow_null=True)
    
    # Плоские поля результатов для удобства
    mean_displacement = serializers.FloatField(source='results.mean_displacement', read_only=True, allow_null=True)
    max_displacement = serializers.FloatField(source='results.max_displacement', read_only=True, allow_null=True)
    median_displacement = serializers.FloatField(source='results.median_displacement', read_only=True, allow_null=True)
    std_displacement = serializers.FloatField(source='results.std_displacement', read_only=True, allow_null=True)
    correlation_quality = serializers.FloatField(source='results.correlation_quality', read_only=True, allow_null=True)
    reliable_points_percentage = serializers.FloatField(source='results.reliable_points_percentage', read_only=True, allow_null=True)
    
    # Вложенные сериализаторы
    sample = SampleSerializer(read_only=True)
    parameters = AnalysisParametersSerializer(read_only=True)
    images = AnalysisImagesSerializer(read_only=True)
    results = AnalysisResultsSerializer(read_only=True)

    class Meta:
        model = AnalysisTask
        fields = [
            'id', 'name', 'status', 'status_display',
            'sample_name', 'material', 'manufacturer', 'test_date',
            'subset_size', 'step', 'max_iter', 'min_correlation',
            'mean_displacement', 'max_displacement', 'median_displacement',
            'std_displacement', 'correlation_quality', 'reliable_points_percentage',
            'sample', 'parameters', 'images', 'results',
            'created_at', 'updated_at',
            'started_at', 'completed_at', 'processing_time',
            'error_message', 'error_traceback'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at',
            'started_at', 'completed_at', 'processing_time',
            'error_message', 'error_traceback'
        ]
