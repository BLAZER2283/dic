import math
import numpy as np
MATERIAL_CHOICES = {
    "ОТ4": "ОТ4 - Титановый сплав",
    "ВТ6": "ВТ6 / ВТ-6 / ВТ6С - Титановый сплав Ti-6Al-4V",
    "ЭП741НП": "ЭП741НП - Жаропрочный никелевый сплав",
}

class PlasmaOptimizer:
    def __init__(self, plasma):
        self.plasma = plasma

    def _normalize(self, s: str) -> str:
        return s.strip().upper().replace("-", "").replace(" ", "")

    def define_material(self, material_type: str) -> str:
        """Определяет материал по типу, используя нормализацию для гибкого сравнения."""
        if not material_type:
            raise ValueError("Material type cannot be empty.")
        normalized_type = self._normalize(material_type)
        
        for key, description in MATERIAL_CHOICES.items():
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
        
        N_segments = math.ceil(length / 50)
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

a = PlasmaOptimizer("ВТ6")
print(a.define_material("ЭП741НП"))
d, l = 20, 700
radius, n, grid = a.geometric_preparation(d, l)
T_profile = a.temperatire_profile(1500, l, 1600, grid)
print(f"Радиус: {radius} м")
print(f"Количество точек: {n}")
print(f"Сетка: {grid}")
print(f"Температурный профиль: {T_profile}")
