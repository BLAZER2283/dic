from django.http import FileResponse, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone
import zipfile
import io
import os
import json
from ..models import AnalysisTask
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def convert_tif_to_png(image_path: str) -> str:
    """Convert TIF/TIFF to PNG if needed."""
    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.tif', '.tiff']:
        try:
            png_path = image_path.rsplit('.', 1)[0] + '.png'
            if not os.path.exists(png_path):
                img = Image.open(image_path)
                img.save(png_path, 'PNG')
            return png_path
        except Exception as e:
            logger.warning("Failed to convert TIF to PNG: %s", e)
            return image_path
    return image_path


class ImageActionsMixin:

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download task results as ZIP archive."""
        instance = self.get_object()

        if instance.status != AnalysisTask.Status.COMPLETED:
            logger.warning("DOWNLOAD: Analysis %s not completed (status: %s)", instance.id, instance.status)
            return Response({"error": "Task is not completed yet"}, status=status.HTTP_400_BAD_REQUEST)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            files_added = 0

            # Images from AnalysisImages
            if hasattr(instance, 'images'):
                images = instance.images

                if images.displacement_map_path:
                    if os.path.exists(images.displacement_map_path):
                        with open(images.displacement_map_path, "rb") as img_file:
                            zip_file.writestr("displacement_map.png", img_file.read())
                        files_added += 1
                    else:
                        logger.warning("DOWNLOAD: Displacement map file not found: %s", images.displacement_map_path)

                if images.image_before and hasattr(images.image_before, "path"):
                    before_path = convert_tif_to_png(images.image_before.path)
                    if os.path.exists(before_path):
                        with open(before_path, "rb") as img_file:
                            zip_file.writestr("original_before.png", img_file.read())
                        files_added += 1
                    else:
                        logger.warning("DOWNLOAD: Before image file not found: %s", before_path)

                if images.image_after and hasattr(images.image_after, "path"):
                    after_path = convert_tif_to_png(images.image_after.path)
                    if os.path.exists(after_path):
                        with open(after_path, "rb") as img_file:
                            zip_file.writestr("original_after.png", img_file.read())
                        files_added += 1
                    else:
                        logger.warning("DOWNLOAD: After image file not found: %s", after_path)

            # Results from AnalysisResults
            if hasattr(instance, 'results') and instance.results.result_json:
                result_json = instance.results.result_json
                if isinstance(result_json, str):
                    json_data = result_json
                else:
                    json_data = json.dumps(result_json, indent=2, ensure_ascii=False)
                zip_file.writestr("analysis_results.json", json_data.encode("utf-8"))
                files_added += 1

            # PDF report
            try:
                from .pdf_generator import DICAnalysisPDFGenerator
                pdf_generator = DICAnalysisPDFGenerator()
                pdf_buffer = pdf_generator.generate_report(instance)
                zip_file.writestr("analysis_report.pdf", pdf_buffer.getvalue())
                files_added += 1
            except Exception as pdf_error:
                logger.exception("DOWNLOAD: Failed to generate PDF report: %s", pdf_error)

            # Summary
            summary = self._generate_summary(instance, request)
            zip_file.writestr("summary.txt", summary.encode("utf-8"))
            files_added += 1

        zip_buffer.seek(0)
        zip_size = len(zip_buffer.getvalue())

        if zip_size == 0:
            logger.warning("DOWNLOAD: Warning - ZIP file is empty!")
            return Response({"error": "No files found to download"}, status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="dic_results_{instance.id}.zip"'
        return response

    @action(detail=True, methods=["get"])
    def image(self, request, pk=None):
        """Get result image."""
        instance = self.get_object()
        image_type = request.query_params.get("type", "displacement")

        image_path = None

        if hasattr(instance, 'images'):
            images = instance.images

            if image_type == "displacement" and images.displacement_map_path:
                image_path = images.displacement_map_path
            elif image_type == "before" and images.image_before:
                image_path = convert_tif_to_png(images.image_before.path)
            elif image_type == "after" and images.image_after:
                image_path = convert_tif_to_png(images.image_after.path)

        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.tif': 'image/tiff',
                '.tiff': 'image/tiff',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
            }
            content_type = mime_types.get(ext, 'application/octet-stream')
            return FileResponse(open(image_path, "rb"), content_type=content_type, as_attachment=False)

        return Response({"error": "Image not found"}, status=404)

    def _generate_summary(self, instance, request):
        """Generate text summary."""
        params = instance.parameters if hasattr(instance, 'parameters') else None
        results = instance.results if hasattr(instance, 'results') else None
        images = instance.images if hasattr(instance, 'images') else None

        return f"""DIC Analysis Results
==========================
Name: {instance.name}
Task ID: {instance.id}
Created: {instance.created_at}
Completed: {instance.completed_at}

Analysis Parameters:
- Window Size: {params.subset_size if params else 'N/A'}
- Step Size: {params.step if params else 'N/A'}
- Max Iterations: {params.max_iter if params else 'N/A'}
- Min Correlation: {params.min_correlation if params else 'N/A'}

Statistics:
- Max Displacement: {results.max_displacement if results and results.max_displacement else 'N/A'}
- Mean Displacement: {results.mean_displacement if results and results.mean_displacement else 'N/A'}
- Median Displacement: {results.median_displacement if results and results.median_displacement else 'N/A'}
- Std Deviation: {results.std_displacement if results and results.std_displacement else 'N/A'}
- Correlation Quality: {results.correlation_quality if results and results.correlation_quality else 'N/A'}
- Reliable Points: {results.reliable_points_percentage if results and results.reliable_points_percentage else 'N/A'}%
- Processing Time: {instance.processing_time if instance.processing_time else 'N/A'} sec

Generated: {timezone.now()}
"""
