import asyncio
import concurrent.futures
from pathlib import Path
import numpy as np
from typing import Tuple, Dict, Any, Optional
import os
import datetime
import json

import logging

from async_dic import AsyncDigitalImageCorrelation
from visualization import save_three_images_sync

logger = logging.getLogger(__name__)

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)


class DICProcessorAPI:
    """
    Асинхронный API процессор для обработки DIC запросов.
    Оптимизирован для средних окон (21-31 пикселя).
    """

    def __init__(self, results_dir: str = "api_results"):
        """
        Инициализация API процессора.
        """
        self.results_dir = results_dir
        self.processing_tasks = {}
        Path(results_dir).mkdir(parents=True, exist_ok=True)

    async def process_test_async(
        self,
        test_id: str,
        img1: np.ndarray,
        img2: np.ndarray,
        subset_size: int = 25,
        step: int = 12,
        max_iter: int = 35,
    ) -> Dict[str, Any]:
        """
        Асинхронная обработка теста с двумя изображениями.
        Оптимальные параметры по умолчанию для средних окон.
        """

        test_dir = os.path.join(self.results_dir, test_id)
        Path(test_dir).mkdir(parents=True, exist_ok=True)

        dic = AsyncDigitalImageCorrelation(
            subset_size=subset_size, step=step, max_iter=max_iter, output_dir=test_dir
        )

        try:
            start_time = datetime.datetime.now()
            U, V, C, x_coords, y_coords, img1_processed, img2_processed = await dic.compute_displacement_field(
                img1, img2
            )

            U_filtered, V_filtered = await dic.post_process_displacements(U, V, C, min_correlation=0.4)

            loop = asyncio.get_event_loop()
            image_paths = await loop.run_in_executor(
                thread_pool,
                save_three_images_sync,
                img1_processed,
                img2_processed,
                U_filtered,
                V_filtered,
                x_coords,
                y_coords,
                test_dir,
                test_id,
            )

            magnitude = np.sqrt(U_filtered**2 + V_filtered**2)
            valid_mask = ~np.isnan(magnitude)
            mag_valid = magnitude[valid_mask]

            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            results = {
                "test_id": test_id,
                "status": "completed",
                "image_paths": image_paths,
                "statistics": {
                    "mean_displacement": float(np.mean(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    "max_displacement": float(np.max(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    "median_displacement": float(np.median(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    "std_displacement": float(np.std(mag_valid)) if len(mag_valid) > 0 else 0.0,
                    "correlation_quality": float(np.mean(C)),
                    "reliable_points_percentage": float(100 * np.sum(C > 0.5) / C.size),
                    "analysis_points": len(x_coords) * len(y_coords),
                    "image_shape": img1.shape,
                    "processing_time_seconds": processing_time,
                    "window_size": subset_size,
                    "step_size": step,
                },
                "parameters": {
                    "subset_size": subset_size,
                    "step": step,
                    "max_iter": max_iter,
                    "min_correlation": 0.4,
                },
                "timestamp": datetime.datetime.now().isoformat(),
            }

            results_path = await dic.save_results_json(test_id, results)
            results["results_json_path"] = results_path

            return results

        except Exception as e:
            error_results = {
                "test_id": test_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat(),
            }
            logger.exception("Ошибка при обработке теста %s: %s", test_id, e)
            return error_results

    async def process_test_from_files_async(
        self,
        test_id: str,
        img1_path: str,
        img2_path: str,
        subset_size: int = 27,
        step: int = 13,
        max_iter: int = 40,
    ) -> Dict[str, Any]:
        """
        Асинхронная обработка теста из файлов изображений.
        Оптимизированные параметры для реальных изображений.
        """
        try:
            img1, img2 = await self._load_images_async(img1_path, img2_path)

            return await self.process_test_async(
                test_id, img1, img2, subset_size=subset_size, step=step, max_iter=max_iter
            )

        except Exception as e:
            return {"test_id": test_id, "status": "error", "error": f"Ошибка загрузки изображений: {e}"}

    async def _load_images_async(self, img1_path: str, img2_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Асинхронная загрузка изображений.
        """
        loop = asyncio.get_event_loop()

        def load_image_sync(path):
            from matplotlib.image import imread

            img = imread(path)
            if len(img.shape) == 3:
                img = np.mean(img, axis=2)
            return img

        img1_task = loop.run_in_executor(thread_pool, load_image_sync, img1_path)
        img2_task = loop.run_in_executor(thread_pool, load_image_sync, img2_path)

        img1, img2 = await asyncio.gather(img1_task, img2_task)

        if img1.shape != img2.shape:
            logger.warning("Размеры изображений различаются: %s vs %s", img1.shape, img2.shape)
            min_height = min(img1.shape[0], img2.shape[0])
            min_width = min(img1.shape[1], img2.shape[1])
            img1 = img1[:min_height, :min_width]
            img2 = img2[:min_height, :min_width]

        return img1, img2

    async def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение результатов теста.
        """
        test_dir = os.path.join(self.results_dir, test_id)
        results_path = os.path.join(test_dir, f"{test_id}_results.json")

        if not os.path.exists(results_path):
            return None

        try:
            with open(results_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}

    async def list_tests(self) -> list:
        """
        Получение списка всех тестов.
        """
        tests = []

        for item in Path(self.results_dir).iterdir():
            if item.is_dir():
                test_id = item.name
                results_path = item / f"{test_id}_results.json"

                if results_path.exists():
                    try:
                        with open(results_path, "r", encoding="utf-8") as f:
                            results = json.load(f)
                        if results and "status" in results:
                            tests.append(
                                {
                                    "test_id": test_id,
                                    "status": results["status"],
                                    "timestamp": results.get("timestamp", ""),
                                    "statistics": results.get("statistics", {}),
                                }
                            )
                    except:
                        continue

        return sorted(tests, key=lambda x: x.get("timestamp", ""), reverse=True)