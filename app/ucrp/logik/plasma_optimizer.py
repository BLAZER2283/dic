from math import ceil
import numpy as np

MATERIAL_CHOICES = {
    "ОТ4": "ОТ4 - Титановый сплав",
    "ВТ6": "ВТ6 / ВТ-6 / ВТ6С - Титановый сплав Ti-6Al-4V",
    "ЭП741НП": "ЭП741НП - Жаропрочный никелевый сплав",
}

MATERIAL_PROPERTIES = {
    "ОТ4": {
        "density": 4500,        # ρ, кг/м³
        "viscosity": 0.0035,    # μ, Па·с
        "t_melt": 1690,         # T_melt, °C
        "t_target": 1780,       # T_target, °C
        "choice": MATERIAL_CHOICES["ОТ4"],
    },
    "ВТ6": {
        "density": 4430,
        "viscosity": 0.0038,
        "t_melt": 1660,
        "t_target": 1750,
        "choice": MATERIAL_CHOICES["ВТ6"],
    },
    "ЭП741НП": {
        "density": 8200,
        "viscosity": 0.0055,
        "t_melt": 1280,
        "t_target": 1380,
        "choice": MATERIAL_CHOICES["ЭП741НП"],
    },
}

class PlasmaOptimizer:
    def __init__(
        self,
        material_type,
        diameter,
        length,
        I_target,
        n_electrode,
        plasma_offset,
        plasma_angle,
        gas_flow,
        pusher_speed,
        vibration_level,
        n_ogark,
        time_from_last_cleaning,
        roller_wear_mm,

        material_choices,
        material_properties,
    ):
        # входные параметры
        self.material_type = material_type
        self.diameter = diameter
        self.length = length
        self.I_target = I_target
        self.n_electrode = n_electrode
        self.plasma_offset = plasma_offset
        self.plasma_angle = plasma_angle
        self.gas_flow = gas_flow
        self.pusher_speed = pusher_speed
        self.vibration_level = vibration_level
        self.n_ogark = n_ogark
        self.time_from_last_cleaning = time_from_last_cleaning
        self.roller_wear_mm = roller_wear_mm

        self.MATERIAL_CHOICES = material_choices
        self.MATERIAL_PROPERTIES = material_properties

        # вычисляемые
        self.material = None
        self.radius = None
        self.n_segments = None
        self.grid = None
        self.T_profile = None
        self.n_profile = None
        self.losses_profile = None
        self.mean_loss = None
        self.d_g_profile = None
        self.d_mean = None
        self.frac = None
        self.stability = None
        self.optimal_I_by_length = None
        self.recommendations = None
        self.warnings = None
    
    def _normalize(self, s: str) -> str:
        return s.strip().upper().replace("-", "").replace(" ", "")

    def define_material(self, material_type: str) -> str:
        """Определяет материал по типу, используя нормализацию для гибкого сравнения."""
        if not material_type:
            raise ValueError("Material type cannot be empty.")
        normalized_type = self._normalize(material_type)
        
        for key, description in self.MATERIAL_PROPERTIES.items():
            if self._normalize(key) == normalized_type:
                return description
        raise ValueError(f"Unknown material type: {material_type}")   
        
        

    def geometric_preparation(self, diameter, length):
        """
        Выполняет геометрическую подготовку электрода.
        """
        if diameter <= 0 or length <= 0:
            raise ValueError("диаметр и длина должны быть положительными числами.")
        R = diameter / 2000.0
        
        N_segments = ceil(length / 50)
        x_grid = np.linspace(0, length, N_segments + 1)
        
        return R, N_segments, x_grid
    
    def temperature_profile(self, I_target, length, T_melt, x_grid):
        """вычисляет температурный профиль вдоль электрода."""
        x = np.array(x_grid, dtype=float)

        base_heat = (I_target / 1400.0) * 200.0

        start_boost = np.exp(-x / 300.0)
        end_loss = np.exp(-(length - x) / 250.0)

        T_profile = T_melt + base_heat * (
            0.75 + 0.15 * start_boost - 0.30 * end_loss
        )

        return T_profile

    def optimization_speed_in_length(self, x_grid, i_target, t_profile, T_target):
        """Оптимизирует скорость перемещения электрода вдоль длины, чтобы поддерживать целевую температуру."""
        x_arr = np.array(x_grid, dtype=float)
        t_arr = np.array(t_profile, dtype=float)
        n_profile = []
        for i, x in enumerate(x_arr):
            if x < 250:
                n = 30100 - 20 * (i_target - 1390)
            elif x <= 480:
                n = 30000
            else:
                delta_n = (
                    100
                    + (i_target - 1390) * 20
                    + (T_target - t_arr[i]) * 5
                )
                n = max(29400, 30000 - delta_n)
            n_profile.append(n)
        return np.array(n_profile)
    
    def size_granul(self, x_grid, I_target, optimal_n_by_length, plasma_offset, diameter, T_profile, p, u):
        """ рассчитать ожидаемый средний размер гранулы (в мкм) для каждого сегмента."""
        d_g_profile = []
        for i, x in enumerate(x_grid):
            n_rpm = optimal_n_by_length[i]
            omega = 2 * np.pi * n_rpm / 60.0
            a = plasma_offset / (diameter / 2)
            t = T_profile[i]
            temp_factor = np.exp(-(t - self.material["t_target"])**2 / (2 * 150**2))
            r = diameter / 2
            d_g = 2.3e5 * u /np.sqrt(p * omega**2 *r) * (1 + 0.018 * (I_target - 1390)) * (1 - 0.2 * a) * temp_factor
            d_g_profile.append(d_g)
        return np.array(d_g_profile)
        
    def loss_forecast(self, i_target, n_electrode, plasma_offset, vibration_level, x_grid):
        """рассчитать ожидаемый процент потерь материала"""
        losses_profile = []

        base_loss = (
            32.1
            + (-0.0215) * i_target
            + 0.00018 * n_electrode
            + 0.045 * plasma_offset
        )

        if vibration_level > 3.2:
            base_loss += 6.3 * (vibration_level - 3.2)

        for x in x_grid:
            if x < 250:
                edge_loss = 2.8
            elif x > 450:   
                edge_loss = 3.6
            else:
                edge_loss = 0

            losses_profile.append(base_loss + edge_loss)

        losses_profile = np.array(losses_profile)
        mean_loss = np.mean(losses_profile)

        return losses_profile, mean_loss

    def fraction_100_140(self, predicted_grain_size, plasma_offset, vibration_level ):
        """Оценить долю гранул размером 100-140 мкм в зависимости от размера гранулы и смещения плазмы."""
        base_frac = 92 * np.exp(-(predicted_grain_size - 120)**2 / (2 * 12**2))
        if plasma_offset > 15:
            base_frac = base_frac * 0.75
        elif plasma_offset > 5:
            base_frac = base_frac * 0.90 
            
        base_frac *= (1 - 0.03 * max(0, vibration_level - 2.0))

        base_frac = max(60, min(98, base_frac))

        return base_frac
    
    def clamp(self, x, min_val, max_val):
        return min(max_val, max(min_val, x))
    
    def index_stability(self, i_target, n_electrode, plasma_offset, vibration_level):
        """Оценить индекс стабильности процесса на основе входных параметров."""
        I_norm = self.clamp((i_target - 1150) / 250, 0, 1)
        n_norm = self.clamp((n_electrode - 29000) / 1500, 0, 1)
        off_norm = self.clamp(plasma_offset / 15.0, 0, 1)
        vib_norm = self.clamp(vibration_level / 6.0, 0, 1)

        penalty = (
            (1 - I_norm) * 20 +
            (1 - n_norm) * 15 +
            off_norm * 30 +
            vib_norm * 35
        )

        stability = self.clamp(100 - penalty, 0, 100)

        return stability

    def generate_warnings_and_recommendations(
        self,
        vibration_level,
        plasma_offset,
        I_target,
        n_electrode,
        plasma_angle,
        time_from_last_cleaning,
        roller_wear_mm,
        length,
        n_ogark,
        gas_flow,
        pusher_speed,
        optimal_I_by_length,
        optimal_n_by_length
    ):
        """на основе всех рассчитанных данных сформировать текстовые советы оператору и выставить флаги предупреждений."""
        recommendations = []
        warnings = {
            "deposits": False,
            "vibration": False,
            "cracking": False,
            "overheating": False
        }

        # Правило 1: Вибрация
        if vibration_level > 3.2:
            warnings["vibration"] = True
            recommendations.append(
                f"⚠ Вибрация {vibration_level} мм/с превышает порог 3.2 мм/с! Рекомендуется остановка."
            )
        elif vibration_level > 2.5:
            recommendations.append(
                f"Вибрация {vibration_level} мм/с — близко к порогу. Контролируйте."
            )

        # Правило 2: Смещение плазмы
        if plasma_offset > 15:
            warnings["deposits"] = True
            recommendations.append(
                f"⚠ Смещение плазмы {plasma_offset} мм слишком велико. Центрируйте плазматрон (допуск ≤1.5 мм)."
            )
        elif plasma_offset > 5:
            recommendations.append(
                f"Смещение плазмы {plasma_offset} мм. Проверьте центровку по лазеру."
            )

        # Правило 3: Риск раскрытия
        if I_target > 1450 and n_electrode < 30000:
            warnings["cracking"] = True
            recommendations.append(
                f"⚠ Высокий ток {I_target} А при скорости {n_electrode} об/мин — риск раскрытия! "
                f"Снизьте ток до ≤1400 А или увеличьте скорость до ≥29500 об/мин."
            )

        # Правило 4: Угол плазмы
        if plasma_angle < 70 or plasma_angle > 95:
            warnings["overheating"] = True
            recommendations.append(
                f"⚠ Нестабильный угол плазмы {plasma_angle}°. Оптимум: 83–86°."
            )
        elif plasma_angle < 80 or plasma_angle > 90:
            recommendations.append(
                f"Угол плазмы {plasma_angle}° — не оптимальный. Рекомендуется 83–86°."
            )

        # Правило 5: Чистка сопла
        if time_from_last_cleaning >= 4:
            warnings["deposits"] = True
            recommendations.append(
                f"Прошло {time_from_last_cleaning} плавок без чистки сопла. Рекомендуется продувка (каждые 4 плавки)."
            )

        # Правило 6: Износ ролика
        if roller_wear_mm > 1.5:
            recommendations.append(
                f"Износ ролика {roller_wear_mm} мм. Рекомендуется замена (норма — каждые 15 плавок)."
            )

        # Правило 7: Скорость огарка
        if length > 500:
            recommendations.append(
                f"На участке >500 мм рекомендуется снизить скорость огарка до {n_ogark} об/мин."
            )

        # Правило 8: Подача газа
        if gas_flow < 2.4:
            recommendations.append(
                f"Расход газа {gas_flow} л/с ниже рекомендуемого (2.6–2.8 л/с). Увеличьте для снижения налипаний."
            )

        # Правило 8a: Толкатель
        if pusher_speed > 48:
            recommendations.append(
                f"Скорость толкателя {pusher_speed} мм/мин выше нормы. "
                f"В начале плавки (x < 250 мм) рекомендуется ≤45 мм/мин."
            )

        # Правило 9: По длине
        if abs(optimal_I_by_length[0] - I_target) > 30:
            recommendations.append(
                f"При x < 250 мм рекомендуется ток {optimal_I_by_length[0]} А "
                f"(отличие от целевого {I_target} А)."
            )

        if optimal_n_by_length[-1] < 29500:
            recommendations.append(
                f"На конце электрода (>500 мм) рекомендуется снизить скорость до "
                f"{optimal_n_by_length[-1]} об/мин."
            )

        return recommendations, warnings

    def calculation_of_optimal_current_by_length(self, x_grid, i_target):
        optimal_I_by_length = []
        for x in x_grid:
            if x < 250:
                i =  i_target - 30
            elif x <= 480:
                i = i_target
            else:
                i = i_target - 40
            optimal_I_by_length.append(i)
        return np.array(optimal_I_by_length)

    def run_all(self):
        # 1. материал
        self.material = self.define_material(self.material_type)

        # 2. геометрия
        self.radius, self.n_segments, self.grid = self.geometric_preparation(
            self.diameter,
            self.length
        )

        # 3. температура
        self.T_profile = self.temperature_profile(
            self.I_target,
            self.length,
            self.material["t_melt"],
            self.grid
        )

        # 4. скорость
        self.n_profile = self.optimization_speed_in_length(
            self.grid,
            self.I_target,
            self.T_profile,
            self.material["t_target"]
        )

        # 5. потери
        self.losses_profile, self.mean_loss = self.loss_forecast(
            self.I_target,
            self.n_electrode,
            self.plasma_offset,
            self.vibration_level,
            self.grid
        )

        # 6. размер гранул
        self.d_g_profile = self.size_granul(
            self.grid,
            self.I_target,
            self.n_profile,
            self.plasma_offset,
            self.diameter,
            self.T_profile,
            self.material["density"],
            self.material["viscosity"]
        )

        self.d_mean = np.mean(self.d_g_profile)

        # 7. фракция
        self.frac = self.fraction_100_140(
            self.d_mean,
            self.plasma_offset,
            self.vibration_level
        )

        # 8. стабильность
        self.stability = self.index_stability(
            self.I_target,
            self.n_electrode,
            self.plasma_offset,
            self.vibration_level
        )

        # 9. оптимальный ток
        self.optimal_I_by_length = self.calculation_of_optimal_current_by_length(
            self.grid,
            self.I_target
        )

        # 10. рекомендации
        self.recommendations, self.warnings = self.generate_warnings_and_recommendations(
            vibration_level=self.vibration_level,
            plasma_offset=self.plasma_offset,
            I_target=self.I_target,
            n_electrode=self.n_electrode,
            plasma_angle=self.plasma_angle,
            time_from_last_cleaning=self.time_from_last_cleaning,
            roller_wear_mm=self.roller_wear_mm,
            length=self.length,
            n_ogark=self.n_ogark,
            gas_flow=self.gas_flow,
            pusher_speed=self.pusher_speed,
            optimal_I_by_length=self.optimal_I_by_length,
            optimal_n_by_length=self.n_profile
        )

        return self

a = PlasmaOptimizer(
    material_type="ОТ4",
    diameter=20,
    length=700,
    I_target=1500,
    n_electrode=30000,
    plasma_offset=10,
    plasma_angle=85,
    gas_flow=2.3,
    pusher_speed=50,
    vibration_level=2.0,
    n_ogark=30000,
    time_from_last_cleaning=5,
    roller_wear_mm=1.2,

    material_choices=MATERIAL_CHOICES,
    material_properties=MATERIAL_PROPERTIES
)
