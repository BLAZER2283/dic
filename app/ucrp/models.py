from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Справочник материалов
MATERIAL_CHOICES = [
    ("ОТ4", "ОТ4 - Титановый сплав"),
    ("ВТ6", "ВТ6 / ВТ-6 / ВТ6С - Титановый сплав Ti-6Al-4V"),
    ("ЭП741НП", "ЭП741НП - Жаропрочный никелевый сплав"),
]

# Физические свойства материалов (зашиты в программу)
MATERIAL_PROPERTIES = {
    "ОТ4": {
        "density": 4500,        # ρ, кг/м³
        "viscosity": 0.0035,    # μ, Па·с
        "t_melt": 1690,         # T_melt, °C
        "t_target": 1780,       # T_target, °C
    },
    "ВТ6": {
        "density": 4430,
        "viscosity": 0.0038,
        "t_melt": 1660,
        "t_target": 1750,
    },
    "ЭП741НП": {
        "density": 8200,
        "viscosity": 0.0055,
        "t_melt": 1280,
        "t_target": 1380,
    },
}


class EPGCalculation(models.Model):
    """
    Основной расчёт ЭПГ (электронно-плазменного гранулирования).
    Связывает все параметры, результаты и рекомендации.
    """

    material = models.CharField(
        max_length=20,
        choices=MATERIAL_CHOICES,
        default="ОТ4",
        verbose_name="Материал (сплав)"
    )
    
    diameter = models.FloatField(
        default=58.0,
        validators=[MinValueValidator(54.0), MaxValueValidator(60.0)],
        verbose_name="Диаметр электрода",
        help_text="мм, диапазон: 54.0–60.0"
    )
    
    length = models.FloatField(
        default=700.0,
        validators=[MinValueValidator(650.0), MaxValueValidator(720.0)],
        verbose_name="Длина электрода",
        help_text="мм, диапазон: 650.0–720.0"
    )
    
    mass_total = models.FloatField(
        default=66.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(300.0)],
        verbose_name="Общая масса электрода",
        help_text="кг (справочное поле)"
    )
    
    I_target = models.FloatField(
        default=1390.0,
        validators=[MinValueValidator(1150.0), MaxValueValidator(1600.0)],
        verbose_name="Целевой ток плазменной дуги",
        help_text="А (Ампер)"
    )
    
    n_electrode = models.FloatField(
        default=30000.0,
        validators=[MinValueValidator(27000.0), MaxValueValidator(34400.0)],
        verbose_name="Скорость вращения электрода",
        help_text="об/мин"
    )
    
    plasma_offset = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(20.0)],
        verbose_name="Смещение плазменной дуги",
        help_text="мм от центра"
    )
    
    plasma_angle = models.FloatField(
        default=86.0,
        validators=[MinValueValidator(70.0), MaxValueValidator(95.0)],
        verbose_name="Угол падения плазменной дуги",
        help_text="градусы"
    )
    
    gas_flow = models.FloatField(
        default=2.6,
        validators=[MinValueValidator(2.0), MaxValueValidator(3.0)],
        verbose_name="Расход защитного газа",
        help_text="л/с"
    )
    
    pusher_speed = models.FloatField(
        default=45.0,
        validators=[MinValueValidator(35.0), MaxValueValidator(60.0)],
        verbose_name="Скорость подачи электрода",
        help_text="мм/мин"
    )

    # ===== Метаданные =====
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата расчёта"
    )

    def get_material_properties(self):
        """Возвращает физические свойства выбранного материала."""
        return MATERIAL_PROPERTIES.get(self.material, MATERIAL_PROPERTIES["ОТ4"])

    class Meta:
        verbose_name = 'Расчёт ЭПГ'
        verbose_name_plural = 'Расчёты ЭПГ'
        ordering = ['-created_at']

    def __str__(self):
        return f"Расчёт ЭПГ #{self.id} - {self.material} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"

    

class EPGAuxiliaryParameters(models.Model):
    """
    Вспомогательные (опциональные) параметры ЭПГ.
    """

    calculation = models.OneToOneField(
        EPGCalculation,
        on_delete=models.CASCADE,
        related_name="auxiliary_params",
        verbose_name="Расчёт"
    )
    
    vibration_level = models.FloatField(
        default=2.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name="Уровень вибрации",
        help_text="мм/с (>3.2 = опасно)"
    )
    
    n_ogark = models.FloatField(
        default=26000.0,
        validators=[MinValueValidator(23000.0), MaxValueValidator(30000.0)],
        verbose_name="Скорость вращения огарка",
        help_text="об/мин"
    )
    
    time_from_last_cleaning = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Плавок с чистки сопла",
        help_text="циклов"
    )
    
    roller_wear_mm = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
        verbose_name="Износ прижимного ролика",
        help_text="мм"
    )
    
    ambient_T = models.FloatField(
        default=20.0,
        validators=[MinValueValidator(10.0), MaxValueValidator(45.0)],
        verbose_name="Температура в цехе",
        help_text="°C (не используется)"
    )

    class Meta:
        verbose_name = 'Вспомогательные параметры ЭПГ'
        verbose_name_plural = 'Вспомогательные параметры ЭПГ'

    def __str__(self):
        return f"Вспом. параметры для расчёта #{self.calculation_id}"


class EPGResults(models.Model):
    """
    Прогнозируемые параметры (output) ЭПГ.
    """

    calculation = models.OneToOneField(
        EPGCalculation,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Расчёт"
    )
    
    predicted_losses_pct = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Прогнозируемые потери",
        help_text="% за плавку, идеал <10%"
    )
    
    predicted_grain_size = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Размер гранулы",
        help_text="мкм, целевой: 100–140"
    )
    
    frac_100_140_pct = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Доля гранул 100–140 мкм",
        help_text="% целевой фракции, идеал >85%"
    )
    
    stability_index = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Индекс стабильности",
        help_text="баллы 0–100"
    )
    
    optimal_I_by_length = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Рекомендуемый ток по длине",
        help_text="массив [float], А"
    )
    
    optimal_n_by_length = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Рекомендуемая скорость по длине",
        help_text="массив [float], об/мин"
    )
    
    x_grid = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Координаты сегментов",
        help_text="массив [float], мм"
    )

    class Meta:
        verbose_name = 'Результаты ЭПГ'
        verbose_name_plural = 'Результаты ЭПГ'

    def __str__(self):
        return f"Результаты для расчёта #{self.calculation_id}"


class EPGWarnings(models.Model):
    """
    Предупреждения (Warning flags) ЭПГ.
    """

    calculation = models.OneToOneField(
        EPGCalculation,
        on_delete=models.CASCADE,
        related_name="warnings_data",
        verbose_name="Расчёт"
    )
    
    deposits = models.BooleanField(
        default=False,
        verbose_name="Риск налипаний",
        help_text="Капли прилипают к стенкам"
    )
    
    vibration = models.BooleanField(
        default=False,
        verbose_name="Превышение вибрации",
        help_text="Вибрация >3.2 мм/с"
    )
    
    cracking = models.BooleanField(
        default=False,
        verbose_name="Риск растрескивания",
        help_text="Риск раскрытия электрода"
    )
    
    overheating = models.BooleanField(
        default=False,
        verbose_name="Перегрев",
        help_text="Температура выше безопасной"
    )

    @property
    def as_dict(self):
        """Возвращает предупреждения как словарь."""
        return {
            "deposits": self.deposits,
            "vibration": self.vibration,
            "cracking": self.cracking,
            "overheating": self.overheating,
        }

    class Meta:
        verbose_name = 'Предупреждения ЭПГ'
        verbose_name_plural = 'Предупреждения ЭПГ'

    def __str__(self):
        return f"Предупреждения для расчёта #{self.calculation_id}"

class EPGInternalData(models.Model):
    """
    3.3 Промежуточные данные (internal) ЭПГ.
    """

    class Meta:
        verbose_name = 'Промежуточные данные ЭПГ'
        verbose_name_plural = 'Промежуточные данные ЭПГ'

    def __str__(self):
        return f"Промежут. данные для расчёта #{self.calculation_id}"

    calculation = models.OneToOneField(
        EPGCalculation,
        on_delete=models.CASCADE,
        related_name="internal_data",
        verbose_name="Расчёт"
    )
    
    T_profile = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Температурный профиль",
        help_text="массив [float], °C"
    )
    
    d_g_profile = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Профиль размера гранул",
        help_text="массив [float], мкм"
    )
    
    losses_profile = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Профиль потерь",
        help_text="массив [float], %"
    )
    
    N_segments = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Количество сегментов",
        help_text="шт (обычно 14–15)"
    )

