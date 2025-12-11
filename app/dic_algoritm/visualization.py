import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, Any

def save_displacement_map_sync(img1: np.ndarray, U: np.ndarray, V: np.ndarray,
                              x_coords: np.ndarray, y_coords: np.ndarray,
                              output_dir: str, filename: str = None) -> str:
    """
    Синхронное сохранение карты смещений БЕЗ ВЕКТОРОВ.
    """
    if filename is None:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"displacement_map_{timestamp}.png"
    
    filepath = os.path.join(output_dir, filename)
    
    # Создаем фигуру для сохранения
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Вычисляем магнитуду смещений
    magnitude = np.sqrt(U**2 + V**2)
    
    # Отображаем тепловую карту смещений на фоне исходного изображения
    ax.imshow(img1, cmap='gray', alpha=0.2, extent=[0, img1.shape[1], img1.shape[0], 0])
    
    # Затем тепловую карту смещений поверх
    im = ax.imshow(magnitude, cmap='hot_r', alpha=0.85,
                  extent=[x_coords[0], x_coords[-1], y_coords[-1], y_coords[0]],
                  vmin=0, vmax=np.nanmax(magnitude))
    
    # Настраиваем график
    ax.set_title('Карта смещений материала\n(красный - большие смещения, синий - малые)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('X (пиксели)', fontsize=12)
    ax.set_ylabel('Y (пиксели)', fontsize=12)
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
    
    # Добавляем цветовую шкалу
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Магнитуда смещений (пиксели)', fontsize=11)
    
    # Добавляем статистику
    stats_text = f"""
    Статистика смещений:
    Среднее: {np.nanmean(magnitude):.3f} пикселей
    Максимум: {np.nanmax(magnitude):.3f} пикселей
    Медиана: {np.nanmedian(magnitude):.3f} пикселей
    Стандартное отклонение: {np.nanstd(magnitude):.3f} пикселей
    """
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Сохраняем с высоким качеством
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return filepath

async def display_results(results: Dict[str, Any]):
    """
    Отображение результатов обработки.
    """
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("=" * 60)
    
    if results['status'] == 'completed':
        print(f"Тест ID: {results['test_id']}")
        print(f"Статус: {results['status']}")
        print(f"Время обработки: {results['statistics']['processing_time_seconds']:.2f} сек")
        
        print(f"\nСОХРАНЕННЫЕ ИЗОБРАЖЕНИЯ:")
        for name, path in results['image_paths'].items():
            print(f"  {name}: {path}")
        
        stats = results['statistics']
        print(f"\nСТАТИСТИКА СМЕЩЕНИЙ:")
        print(f"  Среднее смещение: {stats['mean_displacement']:.4f} пикселей")
        print(f"  Максимальное смещение: {stats['max_displacement']:.4f} пикселей")
        print(f"  Медианное смещение: {stats['median_displacement']:.4f} пикселей")
        print(f"  Стандартное отклонение: {stats['std_displacement']:.4f} пикселей")
        
        print(f"\nКАЧЕСТВО АНАЛИЗА:")
        print(f"  Средняя корреляция: {stats['correlation_quality']:.4f}")
        print(f"  Надежные точки: {stats['reliable_points_percentage']:.1f}%")
        print(f"  Всего точек анализа: {stats['analysis_points']}")
        
        print(f"\nПАРАМЕТРЫ АНАЛИЗА:")
        for key, value in results['parameters'].items():
            print(f"  {key}: {value}")
            
        print(f"\nРезультаты сохранены в: {results['results_json_path']}")
        
    else:
        print(f"Тест ID: {results['test_id']}")
        print(f"Статус: {results['status']}")
        print(f"Ошибка: {results.get('error', 'Неизвестная ошибка')}")


def save_three_images_sync(img1: np.ndarray, img2: np.ndarray, 
                          U: np.ndarray, V: np.ndarray, 
                          x_coords: np.ndarray, y_coords: np.ndarray,
                          output_dir: str, test_id: str) -> Dict[str, str]:
    """
    Синхронное сохранение трех изображений.
    """
    # Вычисляем магнитуду смещений
    magnitude = np.sqrt(U**2 + V**2)
    
    # Сохраняем первое изображение (исходное)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.imshow(img1, cmap='gray')
    ax1.set_title('Исходное изображение (до испытания)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X (пиксели)', fontsize=10)
    ax1.set_ylabel('Y (пиксели)', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    img1_path = os.path.join(output_dir, f"{test_id}_original.png")
    plt.tight_layout()
    plt.savefig(img1_path, dpi=200, bbox_inches='tight')
    plt.close(fig1)
    
    # Сохраняем второе изображение (после деформации)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.imshow(img2, cmap='gray')
    ax2.set_title('Изображение после испытания', fontsize=12, fontweight='bold')
    ax2.set_xlabel('X (пиксели)', fontsize=10)
    ax2.set_ylabel('Y (пиксели)', fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    img2_path = os.path.join(output_dir, f"{test_id}_deformed.png")
    plt.tight_layout()
    plt.savefig(img2_path, dpi=200, bbox_inches='tight')
    plt.close(fig2)
    
    # Сохраняем третье изображение 
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    
    # Показываем тепловую карту смещений
    im = ax3.imshow(magnitude, cmap='hot_r', 
                   extent=[x_coords[0], x_coords[-1], y_coords[-1], y_coords[0]],
                   vmin=0, vmax=np.nanmax(magnitude))
    
    ax3.set_title('Карта смещений\n(красный - большие смещения, белый - малые)', 
                 fontsize=12, fontweight='bold')
    ax3.set_xlabel('X (пиксели)', fontsize=10)
    ax3.set_ylabel('Y (пиксели)', fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Добавляем цветовую шкалу
    cbar = plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    cbar.set_label('Магнитуда смещений (пиксели)', fontsize=10)
    
    # Добавляем статистику
    stats_text = f"""
    Статистика смещений:
    Среднее: {np.nanmean(magnitude):.3f} px
    Максимум: {np.nanmax(magnitude):.3f} px
    Медиана: {np.nanmedian(magnitude):.3f} px
    """
    ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    img3_path = os.path.join(output_dir, f"{test_id}_displacement.png")
    plt.tight_layout()
    plt.savefig(img3_path, dpi=200, bbox_inches='tight')
    plt.close(fig3)
    
    return {
        "original_image": img1_path,
        "deformed_image": img2_path,
        "displacement_map": img3_path
    }
    