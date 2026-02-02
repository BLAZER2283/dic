import logging

from .sync_processor import SyncDICProcessor
from ..models import DICAnalysis


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
            )

            self._update_task_results(task_id, results)

        except Exception:
            import traceback

            traceback.print_exc()

    def _update_task_results(self, task_id, results):
        """
        Обновление результатов задачи в базе данных.
        """
        from django.utils import timezone

        try:
            dic_analysis = DICAnalysis.objects.get(id=task_id)

            if results["status"] == "completed":
                dic_analysis.status = DICAnalysis.Status.COMPLETED

                if "image_paths" in results:
                    image_paths = results["image_paths"]
                    dic_analysis.original_image_path = image_paths.get("original_image", "")
                    dic_analysis.deformed_image_path = image_paths.get("deformed_image", "")
                    dic_analysis.displacement_map_path = image_paths.get("displacement_map", "")

                if "statistics" in results:
                    stats = results["statistics"]
                    dic_analysis.mean_displacement = stats.get("mean_displacement", 0)
                    dic_analysis.max_displacement = stats.get("max_displacement", 0)
                    dic_analysis.median_displacement = stats.get("median_displacement", 0)
                    dic_analysis.std_displacement = stats.get("std_displacement", 0)
                    dic_analysis.correlation_quality = stats.get("correlation_quality", 0)
                    dic_analysis.reliable_points_percentage = stats.get("reliable_points_percentage", 0)
                    dic_analysis.processing_time = stats.get("processing_time_seconds", 0)

                dic_analysis.result_json = results

            else:
                dic_analysis.status = DICAnalysis.Status.ERROR
                dic_analysis.error_message = results.get("error", "Неизвестная ошибка")

            dic_analysis.completed_at = timezone.now()
            dic_analysis.save()

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception("Ошибка при обновлении задачи %s: %s", task_id, e)
    