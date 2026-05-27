import logging
from django.utils import timezone
from .sync_processor import SyncDICProcessor
from ..models import AnalysisTask, AnalysisImages, AnalysisResults


logger = logging.getLogger(__name__)


class HelpMethods:
    """Класс с вспомогательными методами для бизнес логики."""

    def _process_dic_task(self, task_id, img1_path, img2_path, subset_size, step, max_iter, min_correlation):
        """
        Вспомогательный метод для обработки задачи в отдельном потоке.
        """
        try:
            processor = SyncDICProcessor(results_dir="media/results")

            results = processor.process_test_from_files(
                test_id=task_id,
                img1_path=img1_path,
                img2_path=img2_path,
                subset_size=subset_size,
                step=step,
                max_iter=max_iter,
                min_correlation=min_correlation,
            )

            self._update_task_results(task_id, results)

        except Exception:
            import traceback
            traceback.print_exc()

    def _update_task_results(self, task_id, results):
        """
        Обновление результатов задачи в базе данных.
        """
        try:
            # Получаем задачу
            task = AnalysisTask.objects.get(id=task_id)

            if results["status"] == "completed":
                task.status = AnalysisTask.Status.COMPLETED
                task.completed_at = timezone.now()

                # Обновляем изображения (AnalysisImages)
                if hasattr(task, 'images'):
                    images = task.images
                    if "image_paths" in results:
                        image_paths = results["image_paths"]
                        for key in ("original_image", "deformed_image", "displacement_map"):
                            val = image_paths.get(key, "")
                            if val.startswith("media/"):
                                val = val[6:]
                            setattr(images, f"{key}_path", val)
                        images.save()

                # Обновляем результаты (AnalysisResults)
                if hasattr(task, 'results'):
                    results_obj = task.results
                    if "statistics" in results:
                        stats = results["statistics"]
                        results_obj.mean_displacement = stats.get("mean_displacement", 0)
                        results_obj.max_displacement = stats.get("max_displacement", 0)
                        results_obj.median_displacement = stats.get("median_displacement", 0)
                        results_obj.std_displacement = stats.get("std_displacement", 0)
                        results_obj.correlation_quality = stats.get("correlation_quality", 0)
                        results_obj.reliable_points_percentage = stats.get("reliable_points_percentage", 0)
                        results_obj.result_json = results
                        results_obj.save()

                    # Обновляем время обработки в задаче
                    task.processing_time = stats.get("processing_time_seconds", 0)
                    task.save()

            else:
                task.status = AnalysisTask.Status.ERROR
                task.error_message = results.get("error", "Неизвестная ошибка")
                task.completed_at = timezone.now()
                task.save()

        except Exception as e:
            logger.exception("Ошибка при обновлении задачи %s: %s", task_id, e)
    