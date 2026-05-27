
import time
import logging
import traceback
from django.core.management.base import BaseCommand
from django.utils import timezone
from dic_api.models import AnalysisTask
from dic_api.dic_bisnes_logik.sync_processor import SyncDICProcessor
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Запускает воркер для обработки DIC-задач'
    def handle(self, *args, **options):
        self.stdout.write('DIC Worker запущен. Ожидание задач...')
        while True:
            try:
                task = AnalysisTask.objects.filter(status='pending').first()
                if task:
                    self.stdout.write(f'Взял задачу #{task.id}')
                    task.status = 'processing'
                    task.started_at = timezone.now()
                    task.save()
                    try:
                        images = task.images
                        params = task.parameters
                        processor = SyncDICProcessor(results_dir='media/results')
                        results = processor.process_test_from_files(
                            test_id=str(task.id),
                            img1_path=images.image_before.path,
                            img2_path=images.image_after.path,
                            subset_size=params.subset_size,
                            step=params.step,
                            max_iter=params.max_iter,
                            min_correlation=params.min_correlation,
                        )
                        if results['status'] == 'completed':
                            task.status = 'completed'
                            # обновляем изображения
                            if 'image_paths' in results:
                                paths = results['image_paths']
                                for key in ('original_image', 'deformed_image', 'displacement_map'):
                                    val = paths.get(key, '')
                                    if val.startswith('media/'):
                                        val = val[6:]
                                    setattr(images, f'{key}_path', val)
                                images.save()
                            # обновляем результаты
                            if hasattr(task, 'results') and 'statistics' in results:
                                stats = results['statistics']
                                res = task.results
                                res.mean_displacement = stats.get('mean_displacement', 0)
                                res.max_displacement = stats.get('max_displacement', 0)
                                res.median_displacement = stats.get('median_displacement', 0)
                                res.std_displacement = stats.get('std_displacement', 0)
                                res.correlation_quality = stats.get('correlation_quality', 0)
                                res.reliable_points_percentage = stats.get('reliable_points_percentage', 0)
                                res.result_json = results
                                res.save()
                                task.processing_time = stats.get('processing_time_seconds', 0)
                        else:
                            task.status = 'error'
                            task.error_message = results.get('error', 'Неизвестная ошибка')
                        task.completed_at = timezone.now()
                        task.save()
                        self.stdout.write(f'Задача #{task.id} завершена: {task.status}')
                    except Exception as e:
                        logger.exception(f'Ошибка обработки задачи #{task.id}')
                        task.status = 'error'
                        task.error_message = str(e)
                        task.error_traceback = traceback.format_exc()
                        task.completed_at = timezone.now()
                        task.save()
                else:
                    time.sleep(1)
            except Exception as e:
                logger.exception('Ошибка в цикле воркера')
                time.sleep(5)