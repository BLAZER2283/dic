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
    def __init__(self, ):
        pass 
    
    def _normalize(self, s: str) -> str:
        return s.strip().upper().replace("-", "").replace(" ", "")

    def define_material(self, material_type: str) -> str:
        """Определяет материал по типу, используя нормализацию для гибкого сравнения."""
        if not material_type:
            raise ValueError("Material type cannot be empty.")
        normalized_type = self._normalize(material_type)
        
        for key, description in MATERIAL_PROPERTIES.items():
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
            temp_factor = np.exp(-(t - T_target)**2 / (2 * 150**2))
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
    
a = PlasmaOptimizer()
material = a.define_material("ОТ4")
d, l = 20, 700
radius, n, grid = a.geometric_preparation(d, l)
T_profile = a.temperature_profile(1390, 700, 1690, grid)
T_target = 1700 
n_profile = a.optimization_speed_in_length(
    grid,
    1500,
    T_profile,
    T_target
)
losses_profile, mean_loss = a.loss_forecast(
    1500,
    30000,
    10,
    2.0,
    grid
)

d_g_profile = a.size_granul(
    grid,           # x_grid
    1500,           # I_target (тот же, что в оптимизации)
    n_profile,      # optimal_n_by_length
    10,             # plasma_offset (пример)
    d,              # diameter
    T_profile,      # T_profile
    material['density'],            # p (например длина или давление — уточни физический смысл)
    material['viscosity']            # u (скорость/коэф.)
)
d_mean = np.mean(d_g_profile)

frac = a.fraction_100_140(
    d_mean,
    10, 
    2.0
)

stability = a.index_stability(1390, 30000, 0, 2.0)
print(stability)

print(f"Доля фракции 100–140 мкм: {frac:.2f}%")
print(f"Средние потери: {mean_loss:.2f}%")

print(f"Профиль размера гранулы (в мкм): {d_g_profile}")
print(f"Материал: {material}")
print(f"Скорость вращения: {n_profile}")
print(f"Радиус: {radius} м")
print(f"Количество точек: {n}")
print(f"Сетка: {grid}")
print(f"Температурный профиль: {T_profile}")
