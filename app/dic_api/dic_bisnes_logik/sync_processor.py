"""
Синхронный процессор DIC.
"""

import numpy as np
import os
import logging
from pathlib import Path
import json
import datetime
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from dic_algoritm.dic_algorithm import DigitalImageCorrelation

logger = logging.getLogger(__name__)


class SyncDICProcessor:
    """
    Синхронный процессор для DIC анализа.
    """

    def __init__(self, results_dir: str = "sync_results"):
        """
        Инициализация синхронного процессора.
        """
        self.results_dir = results_dir
        Path(results_dir).mkdir(parents=True, exist_ok=True)

    def process_test(self, test_id: str, img1: np.ndarray, img2: np.ndarray, subset_size: int = 25, step: int = 12, max_iter: int = 35) -> dict:
        """
        Синхронная обработка теста.
        """
        test_dir = os.path.join(self.results_dir, test_id)
        Path(test_dir).mkdir(parents=True, exist_ok=True)

        dic = DigitalImageCorrelation(subset_size=subset_size, step=step, max_iter=max_iter)

        try:
            start_time = datetime.datetime.now()

            U, V, C, x_coords, y_coords, img1_processed, img2_processed = dic.compute_displacement_field_sequential(img1, img2)

            U_filtered, V_filtered = dic.post_process_displacements(U, V, C, min_correlation=0.4)

            image_paths = self._save_images_sync(img1_processed, img2_processed, U_filtered, V_filtered, x_coords, y_coords, test_dir, test_id)

            magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
            valid_mask = ~np.isnan(magnitude)
            mag_valid = magnitude[valid_mask]

            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            results = {
                'test_id': test_id,
                'status': 'completed',
                'image_paths': image_paths,
                'statistics': {
                    'mean_displacement': float(np.mean(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    'max_displacement': float(np.max(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    'median_displacement': float(np.median(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    'std_displacement': float(np.std(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    'correlation_quality': float(np.mean(C)),
                    'reliable_points_percentage': float(100 * np.sum(C > 0.5) / C.size),
                    'analysis_points': len(x_coords) * len(y_coords),
                    'image_shape': img1.shape,
                    'processing_time_seconds': processing_time,
                    'window_size': subset_size,
                    'step_size': step
                },
                'parameters': {
                    'subset_size': subset_size,
                    'step': step,
                    'max_iter': max_iter,
                    'min_correlation': 0.4
                },
                'timestamp': datetime.datetime.now().isoformat()
            }

            results_path = os.path.join(test_dir, f"{test_id}_results.json")
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            results['results_json_path'] = results_path

            return results

        except Exception as e:
            error_results = {
                'test_id': test_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }
            logger.exception("Ошибка при обработке теста %s: %s", test_id, e)
            return error_results

    def process_test_from_files(self, test_id: str, img1_path: str, img2_path: str, subset_size: int = 25, step: int = 12, max_iter: int = 35) -> dict:
        """
        Синхронная обработка теста из файлов.
        """
        try:
            img1, img2 = self._load_images_sync(img1_path, img2_path)

            return self.process_test(test_id, img1, img2, subset_size, step, max_iter)

        except Exception as e:
            return {
                'test_id': test_id,
                'status': 'error',
                'error': f"Ошибка загрузки изображений: {e}"
            }

    def _load_images_sync(self, img1_path: str, img2_path: str):
        """
        Синхронная загрузка изображений.
        """
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        img1_array = np.array(img1)
        img2_array = np.array(img2)

        if len(img1_array.shape) == 3:
            img1_array = np.mean(img1_array, axis=2)
        if len(img2_array.shape) == 3:
            img2_array = np.mean(img2_array, axis=2)

        if img1_array.shape != img2_array.shape:
            min_height = min(img1_array.shape[0], img2_array.shape[0])
            min_width = min(img1_array.shape[1], img2_array.shape[1])
            img1_array = img1_array[:min_height, :min_width]
            img2_array = img2_array[:min_height, :min_width]

        return img1_array, img2_array

    def _save_images_sync(self, img1, img2, U, V, x_coords, y_coords, output_dir, test_id):
        """
        Сохранение изображений результатов.
        """
        magnitude = np.sqrt(U**2 + V**2)

        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.imshow(img1, cmap='gray')
        ax1.set_title('Исходное изображение')
        img1_path = os.path.join(output_dir, f"{test_id}_original.png")
        plt.savefig(img1_path, dpi=200, bbox_inches='tight')
        plt.close(fig1)

        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.imshow(img2, cmap='gray')
        ax2.set_title('Изображение после деформации')
        img2_path = os.path.join(output_dir, f"{test_id}_deformed.png")
        plt.savefig(img2_path, dpi=200, bbox_inches='tight')
        plt.close(fig2)

        fig3, ax3 = plt.subplots(figsize=(10, 8))
        im = ax3.imshow(magnitude, cmap='hot_r', extent=[x_coords[0], x_coords[-1], y_coords[-1], y_coords[0]], vmin=0, vmax=np.nanmax(magnitude))
        ax3.set_title('Карта смещений')
        cbar = plt.colorbar(im, ax=ax3)
        cbar.set_label('Магнитуда смещений (пиксели)')
        img3_path = os.path.join(output_dir, f"{test_id}_displacement.png")
        plt.savefig(img3_path, dpi=200, bbox_inches='tight')
        plt.close(fig3)

        return {
            "original_image": img1_path,
            "deformed_image": img2_path,
            "displacement_map": img3_path
        }