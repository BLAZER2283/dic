import asyncio
import concurrent.futures
from pathlib import Path
import numpy as np
from typing import Tuple, Dict, Any
import os
import aiofiles
import json

from dic_algorithm import DigitalImageCorrelation

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

class AsyncDigitalImageCorrelation:
    """
    Асинхронный класс для выполнения Digital Image Correlation (DIC) между двумя изображениями.
    """
    
    def __init__(self, subset_size: int = 25, step: int = 12, max_iter: int = 35, 
                 output_dir: str = "results"):
        """
        Инициализация асинхронного DIC алгоритма.
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
        self.output_dir = output_dir
        
        print(f"Инициализация DIC с параметрами:")
        print(f"  Размер окна: {self.subset_size}px (среднее окно)")
        print(f"  Шаг анализа: {self.step}px")
        print(f"  Макс. итераций: {self.max_iter}")
        
        # Создаем директорию для результатов, если она не существует
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    async def compute_displacement_field(self, img1: np.ndarray, img2: np.ndarray) -> Tuple:
        """
        Асинхронное вычисление поля смещений с оптимальными параметрами.
        """
        dic = DigitalImageCorrelation(self.subset_size, self.step, self.max_iter)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            thread_pool,
            dic.compute_displacement_field,
            img1, img2
        )
    
    async def post_process_displacements(self, U: np.ndarray, V: np.ndarray, C: np.ndarray, 
                                       min_correlation: float = 0.4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Асинхронная постобработка полей смещений.
        Оптимальный порог корреляции для средних окон.
        """
        loop = asyncio.get_event_loop()
        dic = DigitalImageCorrelation(self.subset_size, self.step, self.max_iter)
        return await loop.run_in_executor(
            thread_pool,
            dic.post_process_displacements,
            U, V, C, min_correlation
        )
    
    async def save_results_json(self, test_id: str, results: Dict[str, Any]) -> str:
        """
        Асинхронное сохранение результатов в JSON файл.
        """
        filename = f"{test_id}_results.json"
        filepath = os.path.join(self.output_dir, filename)
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
        
        return filepath