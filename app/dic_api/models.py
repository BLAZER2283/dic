from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class DICAnalysis(models.Model):
    """Модель для хранения задачи анализа DIC."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает обработки'
        PROCESSING = 'processing', 'В процессе'
        COMPLETED = 'completed', 'Завершено'
        ERROR = 'error', 'Ошибка'
        CANCELLED = 'cancelled', 'Отменено'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="DIC Analysis")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Параметры анализа
    subset_size = models.IntegerField(
        default=25,
        validators=[MinValueValidator(21), MaxValueValidator(31)]
    )
    step = models.IntegerField(default=12)
    max_iter = models.IntegerField(default=35)
    min_correlation = models.FloatField(default=0.4)
    
    # Изображения
    image_before = models.ImageField(upload_to='uploads/before/')
    image_after = models.ImageField(upload_to='uploads/after/')
    
    # Результаты
    result_json = models.JSONField(null=True, blank=True)
    result_image_path = models.CharField(max_length=500, null=True, blank=True)
    original_image_path = models.CharField(max_length=500, null=True, blank=True)
    deformed_image_path = models.CharField(max_length=500, null=True, blank=True)
    displacement_map_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Статистика
    mean_displacement = models.FloatField(null=True, blank=True)
    max_displacement = models.FloatField(null=True, blank=True)
    median_displacement = models.FloatField(null=True, blank=True)
    std_displacement = models.FloatField(null=True, blank=True)
    correlation_quality = models.FloatField(null=True, blank=True)
    reliable_points_percentage = models.FloatField(null=True, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  
    
    # Ошибки
    error_message = models.TextField(null=True, blank=True)
    error_traceback = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'DIC анализ'
        verbose_name_plural = 'DIC анализы'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if self.status == self.Status.PROCESSING and not self.started_at:
            from django.utils import timezone
            self.started_at = timezone.now()
        elif self.status == self.Status.COMPLETED and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
            if self.started_at:
                self.processing_time = (self.completed_at - self.started_at).total_seconds()
        
        super().save(*args, **kwargs)