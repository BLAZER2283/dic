from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Sample(models.Model):
    """Модель образца материала."""
    
    name = models.CharField(max_length=255, default="Образец", verbose_name="Наименование образца")
    material = models.CharField(max_length=255, blank=True, null=True, verbose_name="Материал")
    manufacture = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изготовитель")
    test_date = models.DateField(blank=True, null=True, verbose_name="Дата испытания образца")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Образец'
        verbose_name_plural = 'Образцы'

    def __str__(self):
        return f"{self.name} ({self.material})"


class AnalysisTask(models.Model):
    """Модель задачи анализа DIC."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает обработки'
        PROCESSING = 'processing', 'В процессе'
        COMPLETED = 'completed', 'Завершено'
        ERROR = 'error', 'Ошибка'
        CANCELLED = 'cancelled', 'Отменено'

    name = models.CharField(max_length=255, default="DIC Analysis", verbose_name="Название задачи")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Образец"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    error_traceback = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Задача анализа'
        verbose_name_plural = 'Задачи анализа'

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


class AnalysisParameters(models.Model):
    """Параметры алгоритма DIC анализа."""
    
    task = models.OneToOneField(
        AnalysisTask,
        on_delete=models.CASCADE,
        related_name="parameters",
        verbose_name="Задача"
    )
    subset_size = models.IntegerField(
        default=25,
        validators=[MinValueValidator(21), MaxValueValidator(31)],
        verbose_name="Размер подмножества"
    )
    step = models.IntegerField(default=12, verbose_name="Шаг сканирования")
    max_iter = models.IntegerField(default=35, verbose_name="Макс. итераций")
    min_correlation = models.FloatField(default=0.4, verbose_name="Мин. корреляция")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Параметры анализа'
        verbose_name_plural = 'Параметры анализа'

    def __str__(self):
        return f"Параметры для {self.task.name}"


class AnalysisImages(models.Model):
    """Изображения для анализа DIC."""
    
    task = models.OneToOneField(
        AnalysisTask,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Задача"
    )
    image_before = models.ImageField(upload_to='uploads/before/', verbose_name="Изображение до")
    image_after = models.ImageField(upload_to='uploads/after/', verbose_name="Изображение после")
    result_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name="Путь к результату")
    original_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name="Путь к оригиналу")
    deformed_image_path = models.CharField(max_length=500, null=True, blank=True, verbose_name="Путь к деформированному")
    displacement_map_path = models.CharField(max_length=500, null=True, blank=True, verbose_name="Путь к карте перемещений")

    class Meta:
        verbose_name = 'Изображения анализа'
        verbose_name_plural = 'Изображения анализа'

    def __str__(self):
        return f"Изображения для {self.task.name}"


class AnalysisResults(models.Model):
    """Результаты анализа DIC."""
    
    task = models.OneToOneField(
        AnalysisTask,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Задача"
    )
    result_json = models.JSONField(null=True, blank=True, verbose_name="JSON результаты")
    mean_displacement = models.FloatField(null=True, blank=True, verbose_name="Среднее перемещение")
    max_displacement = models.FloatField(null=True, blank=True, verbose_name="Макс. перемещение")
    median_displacement = models.FloatField(null=True, blank=True, verbose_name="Медианное перемещение")
    std_displacement = models.FloatField(null=True, blank=True, verbose_name="Стандартное отклонение")
    correlation_quality = models.FloatField(null=True, blank=True, verbose_name="Качество корреляции")
    reliable_points_percentage = models.FloatField(null=True, blank=True, verbose_name="Процент надёжных точек")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Результат анализа'
        verbose_name_plural = 'Результаты анализа'

    def __str__(self):
        return f"Результаты для {self.task.name}"
    
