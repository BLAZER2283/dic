from django.contrib import admin
from .models import Sample, AnalysisTask, AnalysisParameters, AnalysisImages, AnalysisResults


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    """Админ-панель для образцов."""
    
    list_display = ['name', 'material', 'manufacture', 'test_date', 'created_at']
    list_filter = ['material', 'manufacture']
    search_fields = ['name', 'material', 'manufacture']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    """Админ-панель для задач анализа."""
    
    list_display = ['name', 'sample', 'status', 'created_at', 'completed_at', 'processing_time']
    list_filter = ['status', 'sample__material']
    search_fields = ['name', 'id', 'sample__name']
    readonly_fields = [
        'id', 'created_at', 'updated_at',
        'started_at', 'completed_at', 'processing_time'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'name', 'sample', 'status')
        }),
        ('Временные метки', {
            'fields': (
                'created_at', 'updated_at',
                'started_at', 'completed_at', 'processing_time'
            ),
            'classes': ('collapse',)
        }),
        ('Ошибки', {
            'fields': ('error_message', 'error_traceback'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalysisParameters)
class AnalysisParametersAdmin(admin.ModelAdmin):
    """Админ-панель для параметров анализа."""
    
    list_display = ['task', 'subset_size', 'step', 'max_iter', 'min_correlation', 'created_at']
    list_filter = ['subset_size', 'step']
    search_fields = ['task__name', 'task__id']
    readonly_fields = ['id', 'created_at']


@admin.register(AnalysisImages)
class AnalysisImagesAdmin(admin.ModelAdmin):
    """Админ-панель для изображений."""
    
    list_display = ['task', 'image_before', 'image_after', 'displacement_map_path']
    search_fields = ['task__name', 'task__id']
    readonly_fields = ['id']


@admin.register(AnalysisResults)
class AnalysisResultsAdmin(admin.ModelAdmin):
    """Админ-панель для результатов анализа."""
    
    list_display = [
        'task', 'mean_displacement', 'max_displacement',
        'correlation_quality', 'reliable_points_percentage', 'created_at'
    ]
    list_filter = ['correlation_quality']
    search_fields = ['task__name', 'task__id']
    readonly_fields = ['id', 'created_at']
