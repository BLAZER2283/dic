"""
Асинхронные задачи для обработки DIC анализа.
"""

from django.utils import timezone
from pathlib import Path
import traceback

from .models import DICAnalysis
from .dic_processor import DICProcessorAPI


async def process_dic_analysis(
    task_id: str,
    img1_path: str,
    img2_path: str,
    subset_size: int = 25,
    step: int = 12,
    max_iter: int = 35,
    min_correlation: float = 0.4
):
    """
    Асинхронная функция для обработки DIC анализа.
    """
    try:
        # Получаем задачу
        dic_analysis = await get_dic_analysis(task_id)
        
        # Обновляем статус
        await update_dic_analysis_status(
            task_id,
            DICAnalysis.Status.PROCESSING,
            error_message=None
        )
        
        print(f"Начата обработка задачи {task_id}")
        print(f"Параметры: subset_size={subset_size}, step={step}, max_iter={max_iter}")
        
        # Создаем директорию для результатов
        results_dir = Path('media') / 'results' / task_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем процессор
        processor = DICProcessorAPI(results_dir=str(results_dir))
        
        # Обрабатываем изображения
        results = await processor.process_test_from_files_async(
            test_id=task_id,
            img1_path=img1_path,
            img2_path=img2_path,
            subset_size=subset_size,
            step=step,
            max_iter=max_iter
        )
        
        if results and results['status'] == 'completed':
            # Сохраняем результаты
            await save_dic_analysis_results(task_id, results, str(results_dir))
            
            print(f"Задача {task_id} успешно завершена")
        else:
            error_msg = results.get('error', 'Неизвестная ошибка')
            await update_dic_analysis_status(
                task_id,
                DICAnalysis.Status.ERROR,
                error_message=error_msg
            )
            
    except Exception as e:
        print(f"Ошибка при обработке задачи {task_id}: {str(e)}")
        traceback_str = traceback.format_exc()
        
        await update_dic_analysis_status(
            task_id,
            DICAnalysis.Status.ERROR,
            error_message=str(e),
            error_traceback=traceback_str
        )


async def get_dic_analysis(task_id: str):
    """Получение объекта DICAnalysis асинхронно."""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _get_dic_analysis():
        return DICAnalysis.objects.get(id=task_id)
    
    return await _get_dic_analysis()


async def update_dic_analysis_status(
    task_id: str,
    status: str,
    error_message: str = None,
    error_traceback: str = None
):
    """Обновление статуса DICAnalysis асинхронно."""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _update_status():
        dic_analysis = DICAnalysis.objects.get(id=task_id)
        dic_analysis.status = status
        
        if error_message:
            dic_analysis.error_message = error_message
        if error_traceback:
            dic_analysis.error_traceback = error_traceback
        
        dic_analysis.save()
    
    await _update_status()


async def save_dic_analysis_results(task_id: str, results: dict, results_dir: str):
    """Сохранение результатов DIC анализа асинхронно."""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _save_results():
        dic_analysis = DICAnalysis.objects.get(id=task_id)
        
        # Обновляем статус
        dic_analysis.status = DICAnalysis.Status.COMPLETED
        
        # Сохраняем пути к изображениям
        if 'image_paths' in results:
            image_paths = results['image_paths']
            dic_analysis.original_image_path = image_paths.get('original_image', '')
            dic_analysis.deformed_image_path = image_paths.get('deformed_image', '')
            dic_analysis.displacement_map_path = image_paths.get('displacement_map', '')
        
        # Сохраняем статистику
        if 'statistics' in results:
            stats = results['statistics']
            dic_analysis.mean_displacement = stats.get('mean_displacement', 0)
            dic_analysis.max_displacement = stats.get('max_displacement', 0)
            dic_analysis.median_displacement = stats.get('median_displacement', 0)
            dic_analysis.std_displacement = stats.get('std_displacement', 0)
            dic_analysis.correlation_quality = stats.get('correlation_quality', 0)
            dic_analysis.reliable_points_percentage = stats.get('reliable_points_percentage', 0)
            dic_analysis.processing_time = stats.get('processing_time_seconds', 0)
        
        # Сохраняем параметры и результаты JSON
        dic_analysis.result_json = {
            'results': results,
            'statistics': results.get('statistics', {}),
            'parameters': results.get('parameters', {})
        }
        
        dic_analysis.save()
    
    await _save_results()