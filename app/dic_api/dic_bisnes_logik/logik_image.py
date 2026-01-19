from django.http import FileResponse
from rest_framework.response import Response
from django.utils import timezone
import zipfile
import io
import os
import json
from ..models import DICAnalysis
from rest_framework import status
from django.http import HttpResponse

class ImageActionsMixin:
    
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

            # Генерируем PDF отчет
            print(f"DOWNLOAD: Generating PDF report")
            try:
                from .pdf_generator import DICAnalysisPDFGenerator
                pdf_generator = DICAnalysisPDFGenerator()
                pdf_buffer = pdf_generator.generate_report(instance)
                zip_file.writestr('analysis_report.pdf', pdf_buffer.getvalue())
                files_added += 1
                print(f"DOWNLOAD: PDF report added to ZIP")
            except Exception as pdf_error:
                print(f"DOWNLOAD: Failed to generate PDF report: {pdf_error}")
                # Continue without PDF if generation fails

            # Добавляем статистику в текстовом файле
            print(f"DOWNLOAD: Adding summary text file to ZIP")
            summary = f"""DIC Analysis Results
==========================
Name: {instance.name}
Task ID: {instance.id}
Created: {instance.created_at}
Completed: {instance.completed_at}

Analysis Parameters:
- Window Size: {instance.subset_size}
- Step Size: {instance.step}
- Max Iterations: {instance.max_iter}
- Min Correlation: {instance.min_correlation}

Statistics:
- Max Displacement: {instance.max_displacement if instance.max_displacement else 'N/A'}
- Mean Displacement: {instance.mean_displacement if instance.mean_displacement else 'N/A'}
- Median Displacement: {instance.median_displacement if instance.median_displacement else 'N/A'}
- Std Deviation: {instance.std_displacement if instance.std_displacement else 'N/A'}
- Correlation Quality: {instance.correlation_quality if instance.correlation_quality else 'N/A'}
- Reliable Points: {instance.reliable_points_percentage if instance.reliable_points_percentage else 'N/A'}%
- Processing Time: {instance.processing_time if instance.processing_time else 'N/A'} sec

File Links:
- Before Image: {instance.image_before.url if instance.image_before else 'N/A'}
- After Image: {instance.image_after.url if instance.image_after else 'N/A'}
- Displacement Map: {f"/media/results/{os.path.basename(instance.displacement_map_path)}" if instance.displacement_map_path else 'N/A'}

System Information:
- Host: {request.get_host()}
- Generated: {timezone.now()}
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
    