"""
Тест для проверки DIC алгоритма с идентичными изображениями.
"""
import numpy as np
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dic_algoritm'))

from dic_algorithm import DigitalImageCorrelation

def test_identical_images():
    """Тест: два идентичных изображения должны показывать нулевые смещения."""
    print("=" * 60)
    print("Тест: Идентичные изображения")
    print("=" * 60)
    
    # Создаем тестовое изображение с текстурой
    np.random.seed(42)
    img = np.random.rand(200, 200) * 255
    img = img.astype(np.float32)
    
    # Копируем изображение (идентичное)
    img1 = img.copy()
    img2 = img.copy()
    
    # Инициализируем DIC
    dic = DigitalImageCorrelation(subset_size=25, step=20, max_iter=35)
    
    # Вычисляем смещения
    U, V, C, x_coords, y_coords, img1_proc, img2_proc = dic.compute_displacement_field(img1, img2)
    
    # Постобработка
    U_filtered, V_filtered = dic.post_process_displacements(U, V, C, min_correlation=0.4)
    
    # Статистика
    magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
    
    print(f"\nРазмер изображений: {img1.shape}")
    print(f"Количество точек анализа: {len(x_coords)} x {len(y_coords)} = {len(x_coords) * len(y_coords)}")
    print(f"\nСтатистика смещений:")
    print(f"  Среднее смещение: {np.nanmean(magnitude):.6f} пикселей")
    print(f"  Максимальное смещение: {np.nanmax(magnitude):.6f} пикселей")
    print(f"  Медианное смещение: {np.nanmedian(magnitude):.6f} пикселей")
    print(f"  Стандартное отклонение: {np.nanstd(magnitude):.6f} пикселей")
    print(f"\nКачество корреляции:")
    print(f"  Средняя корреляция: {np.mean(C):.6f}")
    print(f"  Минимальная корреляция: {np.min(C):.6f}")
    print(f"  Максимальная корреляция: {np.max(C):.6f}")
    
    # Проверка
    mean_disp = np.nanmean(magnitude)
    max_disp = np.nanmax(magnitude)
    
    print("\n" + "=" * 60)
    if mean_disp < 0.05 and max_disp < 0.5:
        print("✓ ТЕСТ ПРОЙДЕН: Смещения близки к нулю (как и ожидалось)")
        print(f"  Среднее < 0.05: {mean_disp:.6f}")
        print(f"  Максимум < 0.5: {max_disp:.6f}")
    else:
        print("✗ ТЕСТ НЕ ПРОЙДЕН: Обнаружены ложные смещения!")
        print(f"  Среднее (должно быть < 0.05): {mean_disp:.6f}")
        print(f"  Максимум (должно быть < 0.5): {max_disp:.6f}")
    print("=" * 60)
    
    return mean_disp < 0.05 and max_disp < 0.5


def test_shifted_images():
    """Тест: изображение с известным смещением должно детектироваться."""
    print("\n" + "=" * 60)
    print("Тест: Изображение с известным смещением (2 пикселя вправо)")
    print("=" * 60)
    
    # Создаем тестовое изображение
    np.random.seed(42)
    img1 = np.random.rand(200, 200) * 255
    img1 = img1.astype(np.float32)
    
    # Создаем смещенную копию (сдвиг на 2 пикселя вправо)
    img2 = np.zeros_like(img1)
    img2[:, 2:] = img1[:, :-2]
    img2[:, :2] = img1[:, :2]  # Копируем края для избежания пустых зон
    
    # Инициализируем DIC
    dic = DigitalImageCorrelation(subset_size=25, step=20, max_iter=35)
    
    # Вычисляем смещения
    U, V, C, x_coords, y_coords, img1_proc, img2_proc = dic.compute_displacement_field(img1, img2)
    
    # Постобработка
    U_filtered, V_filtered = dic.post_process_displacements(U, V, C, min_correlation=0.4)
    
    # Статистика
    magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
    
    print(f"\nРазмер изображений: {img1.shape}")
    print(f"Количество точек анализа: {len(x_coords)} x {len(y_coords)} = {len(x_coords) * len(y_coords)}")
    print(f"\nСтатистика смещений:")
    print(f"  Среднее смещение по X: {np.nanmean(U_filtered):.3f} пикселей (ожидалось ~2.0)")
    print(f"  Среднее смещение по Y: {np.nanmean(V_filtered):.3f} пикселей (ожидалось ~0.0)")
    print(f"  Средняя магнитуда: {np.nanmean(magnitude):.3f} пикселей")
    
    # Проверка
    mean_u = np.nanmean(U_filtered)
    mean_v = np.nanmean(V_filtered)
    
    print("\n" + "=" * 60)
    if 1.5 < mean_u < 2.5 and abs(mean_v) < 0.5:
        print("✓ ТЕСТ ПРОЙДЕН: Смещение детектировано корректно")
        print(f"  U ≈ 2.0: {mean_u:.3f}")
        print(f"  V ≈ 0.0: {mean_v:.3f}")
    else:
        print("✗ ТЕСТ НЕ ПРОЙДЕН: Смещение детектировано некорректно!")
        print(f"  U (должно быть 1.5-2.5): {mean_u:.3f}")
        print(f"  V (должно быть < 0.5): {mean_v:.3f}")
    print("=" * 60)
    
    return 1.5 < mean_u < 2.5 and abs(mean_v) < 0.5


if __name__ == "__main__":
    print("\nЗапуск тестов DIC алгоритма...\n")
    
    test1_passed = test_identical_images()
    test2_passed = test_shifted_images()
    
    print("\n\n" + "=" * 60)
    print("ИТОГИ:")
    print(f"  Тест идентичных изображений: {'✓ ПРОЙДЕН' if test1_passed else '✗ НЕ ПРОЙДЕН'}")
    print(f"  Тест смещенных изображений: {'✓ ПРОЙДЕН' if test2_passed else '✗ НЕ ПРОЙДЕН'}")
    print("=" * 60)
    
    sys.exit(0 if (test1_passed and test2_passed) else 1)
