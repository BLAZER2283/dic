"""
Тесты вычислительного ядра DIC (Digital Image Correlation).

Проверяются два опорных свойства алгоритма, которые не зависят от подбора
параметров и должны выполняться всегда:

  * идентичные изображения дают нулевое поле смещений (нет ложного сигнала);
  * искусственно сдвинутое изображение даёт смещение, равное заданному сдвигу.

Второе свойство — это фактически калибровка: если алгоритм не находит
известный сдвиг, доверять его результатам на реальных образцах нельзя.
"""
import numpy as np
import pytest

from dic_algoritm.dic_algorithm import DigitalImageCorrelation

# Алгоритм субпиксельный, поэтому нулевое поле проверяется с допуском на шум.
ZERO_MEAN_TOLERANCE_PX = 0.05
ZERO_MAX_TOLERANCE_PX = 0.5

KNOWN_SHIFT_PX = 2
SHIFT_TOLERANCE_PX = 0.5

MIN_CORRELATION = 0.4


@pytest.fixture
def speckle_image() -> np.ndarray:
    """Синтетическая спекл-текстура с фиксированным seed — тест детерминирован."""
    rng = np.random.default_rng(42)
    return (rng.random((200, 200)) * 255).astype(np.float32)


@pytest.fixture
def dic() -> DigitalImageCorrelation:
    return DigitalImageCorrelation(subset_size=25, step=20, max_iter=35)


def displacement_field(dic, img1, img2):
    """Считает поле смещений и возвращает отфильтрованные U, V и матрицу корреляции."""
    U, V, C, _x, _y, _p1, _p2 = dic.compute_displacement_field(img1, img2)
    U_filtered, V_filtered = dic.post_process_displacements(
        U, V, C, min_correlation=MIN_CORRELATION
    )
    return U_filtered, V_filtered, C


@pytest.mark.slow
def test_identical_images_give_zero_displacement(dic, speckle_image):
    """На идентичных изображениях алгоритм не должен выдумывать смещения."""
    U, V, _ = displacement_field(dic, speckle_image.copy(), speckle_image.copy())
    magnitude = np.sqrt(U**2 + V**2)

    mean_displacement = np.nanmean(magnitude)
    max_displacement = np.nanmax(magnitude)

    assert mean_displacement < ZERO_MEAN_TOLERANCE_PX, (
        f"среднее смещение {mean_displacement:.6f} px "
        f"превышает допуск {ZERO_MEAN_TOLERANCE_PX} px"
    )
    assert max_displacement < ZERO_MAX_TOLERANCE_PX, (
        f"максимальное смещение {max_displacement:.6f} px "
        f"превышает допуск {ZERO_MAX_TOLERANCE_PX} px"
    )


@pytest.mark.slow
def test_identical_images_give_near_perfect_correlation(dic, speckle_image):
    """ZNCC на одинаковых субобластях должен быть практически равен единице."""
    _, _, C = displacement_field(dic, speckle_image.copy(), speckle_image.copy())

    mean_correlation = float(np.mean(C))
    assert mean_correlation > 0.99, (
        f"средняя корреляция {mean_correlation:.6f} слишком низкая для "
        f"идентичных изображений"
    )


@pytest.mark.slow
def test_known_shift_is_measured_correctly(dic, speckle_image):
    """Сдвиг на 2 px вправо должен измеряться как U ≈ 2, V ≈ 0."""
    shifted = np.zeros_like(speckle_image)
    shifted[:, KNOWN_SHIFT_PX:] = speckle_image[:, :-KNOWN_SHIFT_PX]
    # Левый край дублируем, чтобы в кадре не возникла пустая зона без текстуры.
    shifted[:, :KNOWN_SHIFT_PX] = speckle_image[:, :KNOWN_SHIFT_PX]

    U, V, _ = displacement_field(dic, speckle_image, shifted)

    measured_u = np.nanmean(U)
    measured_v = np.nanmean(V)

    assert abs(measured_u - KNOWN_SHIFT_PX) < SHIFT_TOLERANCE_PX, (
        f"измеренный сдвиг по X {measured_u:.3f} px, ожидался {KNOWN_SHIFT_PX} px"
    )
    assert abs(measured_v) < SHIFT_TOLERANCE_PX, (
        f"паразитный сдвиг по Y {measured_v:.3f} px, ожидался 0"
    )
