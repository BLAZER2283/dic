import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import median_filter
from typing import Tuple, Optional
import random

class DigitalImageCorrelation:
    """
    Синхронный класс для выполнения Digital Image Correlation (DIC) между двумя изображениями.
    Оптимизирован для средних окон (21-31 пикселя).
    """
    
    def __init__(self, subset_size: int = 25, step: int = 12, max_iter: int = 35):
        """
        Инициализация DIC алгоритма с оптимальными параметрами для средних окон.
        """
        # Обеспечиваем нечетный размер окна
        self.subset_size = subset_size if subset_size % 2 == 1 else subset_size + 1
        # Проверяем диапазон 21-31
        if self.subset_size < 21:
            self.subset_size = 21
        elif self.subset_size > 31:
            self.subset_size = 31
            
        self.half_subset = self.subset_size // 2
        self.step = step
        self.max_iter = max_iter
        self.tolerance = 1e-6
        
        # Фиксируем seed для воспроизводимости
        np.random.seed(42)
        random.seed(42)
        
        print(f"[DIC] Размер окна: {self.subset_size}px, шаг: {self.step}px, итераций: {self.max_iter}")
    
    def preprocess_images(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Синхронная предварительная обработка изображений.
        """
        # Конвертация в оттенки серого если нужно
        if len(img1.shape) == 3:
            img1 = np.mean(img1, axis=2)
        if len(img2.shape) == 3:
            img2 = np.mean(img2, axis=2)
            
        # Нормализация
        img1 = (img1 - img1.min()) / (img1.max() - img1.min() + 1e-10)
        img2 = (img2 - img2.min()) / (img2.max() - img2.min() + 1e-10)
        
        return img1.astype(np.float32), img2.astype(np.float32)
    
    def zero_mean_normalized_cross_correlation(self, subset1: np.ndarray, subset2: np.ndarray) -> float:
        """
        Вычисляет Zero-mean Normalized Cross-Correlation (ZNCC) между двумя подрегионами.
        """
        # Усреднение по нулевому среднему
        subset1_zero = subset1 - np.mean(subset1)
        subset2_zero = subset2 - np.mean(subset2)
        
        # Вычисление ZNCC
        numerator = np.sum(subset1_zero * subset2_zero)
        denominator = np.sqrt(np.sum(subset1_zero**2) * np.sum(subset2_zero**2))
        
        # Добавление небольшого значения для предотвращения деления на ноль
        return numerator / (denominator + 1e-10)
    
    def bilinear_interpolation(self, img: np.ndarray, x: float, y: float) -> float:
        """
        Билинейная интерполяция для получения значения пикселя в нецелых координатах.
        """
        x0 = int(np.floor(x))
        x1 = x0 + 1
        y0 = int(np.floor(y))
        y1 = y0 + 1
        
        # Проверка границ
        if x0 < 0 or y0 < 0 or x1 >= img.shape[1] or y1 >= img.shape[0]:
            return 0.0
        
        # Коэффициенты интерполяции
        dx = x - x0
        dy = y - y0
        
        # Интерполяция
        value = (img[y0, x0] * (1 - dx) * (1 - dy) +
                img[y0, x1] * dx * (1 - dy) +
                img[y1, x0] * (1 - dx) * dy +
                img[y1, x1] * dx * dy)
        
        return value
    
    def get_subset_interpolated(self, img: np.ndarray, center_x: float, center_y: float) -> np.ndarray:
        """
        Получает подрегион с билинейной интерполяцией.
        Оптимизировано для средних окон.
        """
        subset = np.zeros((self.subset_size, self.subset_size))
        
        # Векторизованный вариант для производительности
        y_indices = np.arange(self.subset_size) - self.half_subset
        x_indices = np.arange(self.subset_size) - self.half_subset
        
        for i in range(self.subset_size):
            y = center_y + y_indices[i]
            if y < 0 or y >= img.shape[0]:
                continue
                
            for j in range(self.subset_size):
                x = center_x + x_indices[j]
                if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
                    subset[i, j] = self.bilinear_interpolation(img, x, y)
        
        return subset
    
    def compute_displacement(self, img1: np.ndarray, img2: np.ndarray, 
                           x: int, y: int, initial_guess: Tuple[float, float] = (0, 0)) -> Tuple[float, float, float]:
        """
        Синхронное вычисление смещения для одной точки.
        Оптимизировано для быстрой сходимости с средними окнами.
        """
        # Получаем подрегион из первого изображения
        subset_ref = self.get_subset_interpolated(img1, x, y)
        
        def objective(params):
            """Функция цели для минимизации (максимизация корреляции)."""
            dx, dy = params
            # Получаем подрегион из второго изображения с учетом смещения
            subset_def = self.get_subset_interpolated(img2, x + dx, y + dy)
            
            # Вычисляем ZNCC (отрицательное, так как мы минимизируем)
            correlation = self.zero_mean_normalized_cross_correlation(subset_ref, subset_def)
            return -correlation  # Минимизируем отрицательную корреляцию
        
        # Ограничения для смещения (увеличены для средних окон)
        bounds = [(-15, 15), (-15, 15)]
        
        # Оптимизация для нахождения лучшего смещения
        result = minimize(objective, initial_guess, method='L-BFGS-B', 
                         bounds=bounds, 
                         options={'maxiter': self.max_iter, 'gtol': 1e-8, 'ftol': 1e-8},
                         tol=self.tolerance)
        
        dx, dy = result.x
        correlation = -result.fun  # Положительное значение корреляции
        
        return dx, dy, correlation
    
    def compute_displacement_field_sequential(self, img1: np.ndarray, img2: np.ndarray) -> Tuple:
        """
        Синхронное вычисление поля смещений для всего изображения.
        Последовательный расчет для детерминированности и стабильности.
        """
        # Предобработка изображений
        img1, img2 = self.preprocess_images(img1, img2)
        
        # Создаем сетку точек для анализа
        height, width = img1.shape
        y_coords = np.arange(self.half_subset, height - self.half_subset, self.step)
        x_coords = np.arange(self.half_subset, width - self.half_subset, self.step)
        
        # Инициализация полей
        U = np.zeros((len(y_coords), len(x_coords)))
        V = np.zeros((len(y_coords), len(x_coords)))
        C = np.zeros((len(y_coords), len(x_coords)))
        
        print(f"Вычисление поля смещений для {len(y_coords)}x{len(x_coords)} точек...")
        print(f"Всего точек анализа: {len(y_coords) * len(x_coords)}")
        
        # Вычисление смещений для каждой точки ПОСЛЕДОВАТЕЛЬНО
        # Это важно для детерминированности и использования предыдущих результатов
        for i, y in enumerate(y_coords):
            for j, x in enumerate(x_coords):
                # Используем (0, 0) как начальное приближение для детерминированности
                initial_guess = (0.0, 0.0)
                
                dx, dy, correlation = self.compute_displacement(img1, img2, x, y, initial_guess)
                U[i, j] = dx
                V[i, j] = dy
                C[i, j] = correlation
                
                # Прогресс-бар
                if (i * len(x_coords) + j) % 100 == 0 and (i * len(x_coords) + j) > 0:
                    progress = (i * len(x_coords) + j) / (len(y_coords) * len(x_coords)) * 100
                    print(f"Прогресс: {progress:.1f}% ({i * len(x_coords) + j}/{len(y_coords) * len(x_coords)})")
        
        print(f"Вычисление завершено!")
        print(f"Средняя корреляция: {np.mean(C):.4f}")
        print(f"Максимальная корреляция: {np.max(C):.4f}")
        
        return U, V, C, x_coords, y_coords, img1, img2
    
    def compute_displacement_field(self, img1: np.ndarray, img2: np.ndarray) -> Tuple:
        """
        Алиас для совместимости с существующим кодом.
        """
        return self.compute_displacement_field_sequential(img1, img2)
    
    def post_process_displacements(self, U: np.ndarray, V: np.ndarray, C: np.ndarray, 
                                 min_correlation: float = 0.4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Синхронная постобработка полей смещений.
        Оптимальный порог корреляции для средних окон.
        """
        # Создаем копии для избежания модификации оригинальных данных
        U_filtered = U.copy()
        V_filtered = V.copy()
        
        print(f"Постобработка с порогом корреляции: {min_correlation}")
        
        # Фильтрация по корреляции
        mask = C > min_correlation
        valid_points = np.sum(mask)
        total_points = C.size
        
        print(f"Надежные точки: {valid_points}/{total_points} ({100 * valid_points/total_points:.1f}%)")
        
        U_filtered[~mask] = np.nan
        V_filtered[~mask] = np.nan
        
        # Медианная фильтрация для удаления выбросов
        # Используем fixed mode для детерминированности
        U_filtered = median_filter(U_filtered, size=3, mode='constant', cval=np.nan)
        V_filtered = median_filter(V_filtered, size=3, mode='constant', cval=np.nan)
        
        # Статистика смещений
        magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
        valid_mag = magnitude[~np.isnan(magnitude)]
        
        if len(valid_mag) > 0:
            print(f"Статистика смещений после фильтрации:")
            print(f"  Среднее: {np.mean(valid_mag):.3f} px")
            print(f"  Максимум: {np.max(valid_mag):.3f} px")
            print(f"  Медиана: {np.median(valid_mag):.3f} px")
            print(f"  Стандартное отклонение: {np.std(valid_mag):.3f} px")
        
        return U_filtered, V_filtered