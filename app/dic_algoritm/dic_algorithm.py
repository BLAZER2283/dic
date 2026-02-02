import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import median_filter
from typing import Tuple
import random
import logging

logger = logging.getLogger(__name__)


class DigitalImageCorrelation:
    """
    Синхронный класс для выполнения Digital Image Correlation (DIC) между двумя изображениями.
    Оптимизирован для средних окон (21-31 пикселя).
    """

    def __init__(self, subset_size: int = 25, step: int = 12, max_iter: int = 35):
        """
        Инициализация DIC алгоритма с оптимальными параметрами для средних окон.
        """
        self.subset_size = subset_size if subset_size % 2 == 1 else subset_size + 1
        if self.subset_size < 21:
            self.subset_size = 21
        elif self.subset_size > 31:
            self.subset_size = 31

        self.half_subset = self.subset_size // 2
        self.step = step
        self.max_iter = max_iter
        self.tolerance = 1e-6

        np.random.seed(42)
        random.seed(42)

    def preprocess_images(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Синхронная предварительная обработка изображений.
        """
        if len(img1.shape) == 3:
            img1 = np.mean(img1, axis=2)
        if len(img2.shape) == 3:
            img2 = np.mean(img2, axis=2)

        img1 = (img1 - img1.min()) / (img1.max() - img1.min() + 1e-10)
        img2 = (img2 - img2.min()) / (img2.max() - img2.min() + 1e-10)

        return img1.astype(np.float32), img2.astype(np.float32)

    def zero_mean_normalized_cross_correlation(self, subset1: np.ndarray, subset2: np.ndarray) -> float:
        """
        Вычисляет Zero-mean Normalized Cross-Correlation (ZNCC) между двумя подрегионами.
        """
        subset1_zero = subset1 - np.mean(subset1)
        subset2_zero = subset2 - np.mean(subset2)

        numerator = np.sum(subset1_zero * subset2_zero)
        denominator = np.sqrt(np.sum(subset1_zero**2) * np.sum(subset2_zero**2))

        return numerator / (denominator + 1e-10)

    def bilinear_interpolation(self, img: np.ndarray, x: float, y: float) -> float:
        """
        Билинейная интерполяция для получения значения пикселя в нецелых координатах.
        """
        x0 = int(np.floor(x))
        x1 = x0 + 1
        y0 = int(np.floor(y))
        y1 = y0 + 1

        if x0 < 0 or y0 < 0 or x1 >= img.shape[1] or y1 >= img.shape[0]:
            return 0.0

        dx = x - x0
        dy = y - y0

        value = (
            img[y0, x0] * (1 - dx) * (1 - dy)
            + img[y0, x1] * dx * (1 - dy)
            + img[y1, x0] * (1 - dx) * dy
            + img[y1, x1] * dx * dy
        )

        return value

    def get_subset_interpolated(self, img: np.ndarray, center_x: float, center_y: float) -> np.ndarray:
        """
        Получает подрегион с билинейной интерполяцией.
        Оптимизировано для средних окон.
        """
        subset = np.zeros((self.subset_size, self.subset_size))

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

    def compute_displacement(
        self,
        img1: np.ndarray,
        img2: np.ndarray,
        x: int,
        y: int,
        initial_guess: Tuple[float, float] = (0, 0),
    ) -> Tuple[float, float, float]:
        """
        Синхронное вычисление смещения для одной точки.
        Оптимизировано для быстрой сходимости с средними окнами.
        """
        subset_ref = self.get_subset_interpolated(img1, x, y)

        def objective(params):
            dx, dy = params
            subset_def = self.get_subset_interpolated(img2, x + dx, y + dy)
            correlation = self.zero_mean_normalized_cross_correlation(subset_ref, subset_def)
            return -correlation

        bounds = [(-15, 15), (-15, 15)]

        result = minimize(
            objective,
            initial_guess,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": self.max_iter, "gtol": 1e-8, "ftol": 1e-8},
            tol=self.tolerance,
        )

        dx, dy = result.x
        correlation = -result.fun

        return dx, dy, correlation

    def compute_displacement_field_sequential(self, img1: np.ndarray, img2: np.ndarray) -> Tuple:
        """
        Синхронное вычисление поля смещений для всего изображения.
        Последовательный расчет для детерминированности и стабильности.
        """
        img1, img2 = self.preprocess_images(img1, img2)

        height, width = img1.shape
        y_coords = np.arange(self.half_subset, height - self.half_subset, self.step)
        x_coords = np.arange(self.half_subset, width - self.half_subset, self.step)

        U = np.zeros((len(y_coords), len(x_coords)))
        V = np.zeros((len(y_coords), len(x_coords)))
        C = np.zeros((len(y_coords), len(x_coords)))

        for i, y in enumerate(y_coords):
            for j, x in enumerate(x_coords):
                initial_guess = (0.0, 0.0)

                dx, dy, correlation = self.compute_displacement(img1, img2, x, y, initial_guess)
                U[i, j] = dx
                V[i, j] = dy
                C[i, j] = correlation

                if (i * len(x_coords) + j) % 100 == 0 and (i * len(x_coords) + j) > 0:
                    processed = (i * len(x_coords) + j)
                    total = len(y_coords) * len(x_coords)
                    progress = processed / total * 100
                    logger.info(f"Прогресс: {progress:.1f}% ({processed}/{total})")

        return U, V, C, x_coords, y_coords, img1, img2

    def compute_displacement_field(self, img1: np.ndarray, img2: np.ndarray) -> Tuple:
        """
        Алиас для совместимости с существующим кодом.
        """
        return self.compute_displacement_field_sequential(img1, img2)

    def post_process_displacements(
        self, U: np.ndarray, V: np.ndarray, C: np.ndarray, min_correlation: float = 0.4
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Синхронная постобработка полей смещений.
        Оптимальный порог корреляции для средних окон.
        """
        U_filtered = U.copy()
        V_filtered = V.copy()

        mask = C > min_correlation
        valid_points = np.sum(mask)
        total_points = C.size

        U_filtered[~mask] = np.nan
        V_filtered[~mask] = np.nan

        U_filtered = median_filter(U_filtered, size=3, mode="constant", cval=np.nan)
        V_filtered = median_filter(V_filtered, size=3, mode="constant", cval=np.nan)

        magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
        valid_mag = magnitude[~np.isnan(magnitude)]

        if len(valid_mag) > 0:
            return U_filtered, V_filtered