from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import rest_framework
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import os
from django.db import models
import threading  
import zipfile
import io
import json
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.conf import settings
import json
from .models import DICAnalysis
from .serealisers import DICAnalysisSerializer, DICAnalysisCreateSerializer
from .sync_processor import SyncDICProcessor
from django.http import JsonResponse
from django.middleware.csrf import get_token


class StandardPagination(PageNumberPagination):
    """Стандартная пагинация."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DICAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с задачами DIC анализа.
    Поддерживает создание, просмотр статуса и результатов.
    """

    queryset = DICAnalysis.objects.all().order_by('-created_at')
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardPagination
    filterset_fields = ['status']
    search_fields = ['name', 'id']
    ordering_fields = ['created_at', 'completed_at', 'processing_time', 'max_displacement']
    permission_classes = [rest_framework.permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DICAnalysisCreateSerializer
        return DICAnalysisSerializer
    
    @method_decorator(csrf_exempt)
    def create(self, request, *args, **kwargs):
        """Создание новой задачи анализа."""
        print(f"DEBUG: Create request data keys: {list(request.data.keys())}")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request content type: {request.content_type}")

        serializer = self.get_serializer(data=request.data)
        print(f"DEBUG: Serializer is valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        
        # Создаем задачу
        dic_analysis = serializer.save()
        
        # Запускаем обработку в отдельном потоке
        task_id = str(dic_analysis.id)
        
        # Создаем поток для обработки
        thread = threading.Thread(
            target=self._process_dic_task,
            args=(
                task_id,
                dic_analysis.image_before.path,
                dic_analysis.image_after.path,
                dic_analysis.subset_size,
                dic_analysis.step,
                dic_analysis.max_iter,
                dic_analysis.min_correlation
            ),
            daemon=True
        )
        thread.start()
        
        # Возвращаем информацию о созданной задаче
        response_serializer = DICAnalysisSerializer(
            dic_analysis,
            context={'request': request}
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def list(self, request, *args, **kwargs):
        """Получение списка всех задач с фильтрацией."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Дополнительная фильтрация по дате
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Дополнительная фильтрация по наличию результатов
        has_results = request.query_params.get('has_results')
        if has_results == 'true':
            queryset = queryset.filter(displacement_map_path__isnull=False)
        elif has_results == 'false':
            queryset = queryset.filter(displacement_map_path__isnull=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Получение деталей задачи с абсолютными URL."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Добавляем абсолютные URL для изображений
        if instance.displacement_map_path:
            data['displacement_map_url'] = request.build_absolute_uri(
                instance.displacement_map_path.url
            )
        
        if instance.image_before:
            data['image_before_url'] = request.build_absolute_uri(
                instance.image_before.url
            )
        
        if instance.image_after:
            data['image_after_url'] = request.build_absolute_uri(
                instance.image_after.url
            )
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена выполнения задачи."""
        dic_analysis = self.get_object()
        
        if dic_analysis.status not in [DICAnalysis.Status.COMPLETED, DICAnalysis.Status.ERROR]:
            dic_analysis.status = DICAnalysis.Status.CANCELLED
            dic_analysis.save()
            return Response(
                {'message': 'Задача успешно отменена'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Невозможно отменить завершенную или ошибочную задачу'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Скачивание результатов задачи в ZIP архиве."""
        instance = self.get_object()
        print(f"DOWNLOAD: Request for analysis {instance.id}, status: {instance.status}")

        if instance.status != DICAnalysis.Status.COMPLETED:
            print(f"DOWNLOAD: Analysis {instance.id} not completed (status: {instance.status})")
            return Response(
                {'error': 'Задача еще не завершена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"DOWNLOAD: Analysis {instance.id} is completed, preparing ZIP file")
        
        # Создаем ZIP архив в памяти
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            files_added = 0

            # Добавляем изображение карты смещений
            if instance.displacement_map_path:
                displacement_path = instance.displacement_map_path
                print(f"DOWNLOAD: Checking displacement map: {displacement_path}")
                if os.path.exists(displacement_path):
                    print(f"DOWNLOAD: Adding displacement map to ZIP")
                    with open(displacement_path, 'rb') as img_file:
                        zip_file.writestr('displacement_map.png', img_file.read())
                    files_added += 1
                else:
                    print(f"DOWNLOAD: Displacement map file not found: {displacement_path}")

            # Добавляем оригинальные изображения
            if instance.image_before and hasattr(instance.image_before, 'path'):
                before_path = instance.image_before.path
                print(f"DOWNLOAD: Checking before image: {before_path}")
                if os.path.exists(before_path):
                    print(f"DOWNLOAD: Adding before image to ZIP")
                    with open(before_path, 'rb') as img_file:
                        zip_file.writestr('original_before.png', img_file.read())
                    files_added += 1
                else:
                    print(f"DOWNLOAD: Before image file not found: {before_path}")

            if instance.image_after and hasattr(instance.image_after, 'path'):
                after_path = instance.image_after.path
                print(f"DOWNLOAD: Checking after image: {after_path}")
                if os.path.exists(after_path):
                    print(f"DOWNLOAD: Adding after image to ZIP")
                    with open(after_path, 'rb') as img_file:
                        zip_file.writestr('original_after.png', img_file.read())
                    files_added += 1
                else:
                    print(f"DOWNLOAD: After image file not found: {after_path}")

            # Добавляем данные в JSON
            if instance.result_json:
                print(f"DOWNLOAD: Adding JSON results to ZIP")
                if isinstance(instance.result_json, str):
                    json_data = instance.result_json
                else:
                    json_data = json.dumps(instance.result_json, indent=2, ensure_ascii=False)
                zip_file.writestr('analysis_results.json', json_data.encode('utf-8'))
                files_added += 1

            # Добавляем статистику в текстовом файле
            print(f"DOWNLOAD: Adding summary text file to ZIP")
            summary = f"""Результаты анализа DIC
==========================
Название: {instance.name}
ID задачи: {instance.id}
Дата создания: {instance.created_at}
Дата завершения: {instance.completed_at}

Параметры анализа:
- Размер окна: {instance.subset_size}
- Шаг анализа: {instance.step}
- Макс. итераций: {instance.max_iter}
- Минимальная корреляция: {instance.min_correlation}

Статистика:
- Максимальное смещение: {instance.max_displacement if instance.max_displacement else 'Н/Д'}
- Среднее смещение: {instance.mean_displacement if instance.mean_displacement else 'Н/Д'}
- Медианное смещение: {instance.median_displacement if instance.median_displacement else 'Н/Д'}
- Стандартное отклонение: {instance.std_displacement if instance.std_displacement else 'Н/Д'}
- Качество корреляции: {instance.correlation_quality if instance.correlation_quality else 'Н/Д'}
- Надежные точки: {instance.reliable_points_percentage if instance.reliable_points_percentage else 'Н/Д'}%
- Время обработки: {instance.processing_time if instance.processing_time else 'Н/Д'} сек

Ссылки на файлы:
- Изображение до деформации: {instance.image_before.url if instance.image_before else 'Н/Д'}
- Изображение после деформации: {instance.image_after.url if instance.image_after else 'Н/Д'}
- Карта смещений: {f"/media/results/{os.path.basename(instance.displacement_map_path)}" if instance.displacement_map_path else 'Н/Д'}

Системная информация:
- Имя хоста: {request.get_host()}
- Время генерации: {timezone.now()}
"""
            
            zip_file.writestr('summary.txt', summary.encode('utf-8'))
            files_added += 1

        zip_buffer.seek(0)
        zip_size = len(zip_buffer.getvalue())
        print(f"DOWNLOAD: ZIP file created with {files_added} files, size: {zip_size} bytes")

        if zip_size == 0:
            print(f"DOWNLOAD: Warning - ZIP file is empty!")
            return Response(
                {'error': 'No files found to download'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Возвращаем ZIP архив как ответ
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="dic_results_{instance.id}.zip"'
        print(f"DOWNLOAD: Sending ZIP file to client")
        return response
    
    @action(detail=True, methods=['get'])
    def image(self, request, pk=None):
        """Получение изображения результатов."""
        instance = self.get_object()
        image_type = request.query_params.get('type', 'displacement')
        
        image_path = None
        
        if image_type == 'displacement' and instance.displacement_map_path:
            image_path = instance.displacement_map_path
        elif image_type == 'before' and instance.image_before:
            image_path = instance.image_before.path
        elif image_type == 'after' and instance.image_after:
            image_path = instance.image_after.path
        
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            content_type = f'image/{ext[1:]}' if ext else 'image/png'
            
            return FileResponse(
                open(image_path, 'rb'),
                content_type=content_type,
                as_attachment=False
            )
        
        return Response({'error': 'Изображение не найдено'}, status=404)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получение статистики по всем задачам."""
        total = self.get_queryset().count()
        completed = self.get_queryset().filter(status=DICAnalysis.Status.COMPLETED).count()
        processing = self.get_queryset().filter(status=DICAnalysis.Status.PROCESSING).count()
        pending = self.get_queryset().filter(status=DICAnalysis.Status.PENDING).count()
        error = self.get_queryset().filter(status=DICAnalysis.Status.ERROR).count()
        cancelled = self.get_queryset().filter(status=DICAnalysis.Status.CANCELLED).count()
        
        # Статистика по времени обработки
        completed_tasks = self.get_queryset().filter(status=DICAnalysis.Status.COMPLETED)
        
        if completed_tasks.exists():
            avg_processing_time = completed_tasks.aggregate(
                avg=models.Avg('processing_time')
            )['avg'] or 0
            
            total_processing_time = completed_tasks.aggregate(
                total=models.Sum('processing_time')
            )['total'] or 0
            
            # Статистика по деформациям
            avg_max_displacement = completed_tasks.aggregate(
                avg=models.Avg('max_displacement')
            )['avg'] or 0
            
            avg_mean_displacement = completed_tasks.aggregate(
                avg=models.Avg('mean_displacement')
            )['avg'] or 0
            
            # Последние завершенные задачи
            recent_tasks = completed_tasks.order_by('-completed_at')[:5]
            recent_serializer = self.get_serializer(recent_tasks, many=True)
            recent_data = recent_serializer.data
        else:
            avg_processing_time = 0
            total_processing_time = 0
            avg_max_displacement = 0
            avg_mean_displacement = 0
            recent_data = []
        
        # Статистика по времени
        timeline = {
            'last_24_hours': self.get_queryset().filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count(),
            'last_week': self.get_queryset().filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'last_month': self.get_queryset().filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        return Response({
            'overview': {
                'total': total,
                'completed': completed,
                'processing': processing,
                'pending': pending,
                'error': error,
                'cancelled': cancelled,
                'success_rate': round((completed / total * 100) if total > 0 else 0, 1)
            },
            'processing_stats': {
                'avg_processing_time': round(avg_processing_time, 2),
                'total_processing_time': round(total_processing_time, 2)
            },
            'deformation_stats': {
                'avg_max_displacement': round(avg_max_displacement, 3),
                'avg_mean_displacement': round(avg_mean_displacement, 3)
            },
            'recent_tasks': recent_data,
            'timeline': timeline
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Получение последних задач."""
        recent_tasks = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Массовое удаление задач."""
        task_ids = request.data.get('task_ids', [])
        
        if not task_ids:
            return Response(
                {'error': 'Не указаны ID задач для удаления'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Фильтруем только существующие задачи
        tasks_to_delete = self.get_queryset().filter(id__in=task_ids)
        deleted_count = tasks_to_delete.count()
        
        # Удаляем задачи
        tasks_to_delete.delete()
        
        return Response({
            'message': f'Удалено {deleted_count} задач',
            'deleted_count': deleted_count
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Краткая сводка по задачам."""
        total = self.get_queryset().count()
        completed = self.get_queryset().filter(status=DICAnalysis.Status.COMPLETED).count()
        
        # Последние 5 задач
        latest_tasks = self.get_queryset()[:5]
        latest_serializer = self.get_serializer(latest_tasks, many=True)
        
        # Задачи в обработке
        processing_tasks = self.get_queryset().filter(status=DICAnalysis.Status.PROCESSING)
        processing_serializer = self.get_serializer(processing_tasks, many=True)
        
        return Response({
            'total_tasks': total,
            'completed_tasks': completed,
            'success_rate': round((completed / total * 100) if total > 0 else 0, 1),
            'latest_tasks': latest_serializer.data,
            'processing_tasks': processing_serializer.data,
            'tasks_by_status': {
                'pending': self.get_queryset().filter(status=DICAnalysis.Status.PENDING).count(),
                'processing': processing_tasks.count(),
                'completed': completed,
                'error': self.get_queryset().filter(status=DICAnalysis.Status.ERROR).count(),
                'cancelled': self.get_queryset().filter(status=DICAnalysis.Status.CANCELLED).count()
            }
        })
    
    def _process_dic_task(self, task_id, img1_path, img2_path,
                         subset_size, step, max_iter, min_correlation):
        """
        Вспомогательный метод для обработки задачи в отдельном потоке.
        """
        try:
            # Создаем синхронный процессор
            processor = SyncDICProcessor(results_dir="media/results")
            
            # Обрабатываем изображения
            results = processor.process_test_from_files(
                test_id=task_id,
                img1_path=img1_path,
                img2_path=img2_path,
                subset_size=subset_size,
                step=step,
                max_iter=max_iter
            )
            
            # Обновляем модель с результатами
            self._update_task_results(task_id, results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _update_task_results(self, task_id, results):
        """
        Обновление результатов задачи в базе данных.
        """
        from django.utils import timezone
        
        try:
            dic_analysis = DICAnalysis.objects.get(id=task_id)
            
            if results['status'] == 'completed':
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
                
                # Сохраняем JSON
                dic_analysis.result_json = results
                
            else:
                dic_analysis.status = DICAnalysis.Status.ERROR
                dic_analysis.error_message = results.get('error', 'Неизвестная ошибка')
            
            dic_analysis.completed_at = timezone.now()
            dic_analysis.save()
            
        except Exception as e:
            print(f"Ошибка при обновлении задачи {task_id}: {e}")

@require_POST
@csrf_exempt
def register_view(request):
    """Регистрация нового пользователя."""
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except:
        username = request.POST.get('username')
        password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@csrf_exempt
def login_view(request):
    """Вход пользователя."""
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except:
        username = request.POST.get('username')
        password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)


@require_POST
@csrf_exempt
def logout_view(request):
    """Выход пользователя."""
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})


def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


