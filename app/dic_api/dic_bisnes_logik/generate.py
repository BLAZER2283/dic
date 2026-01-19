from rest_framework.decorators import action
from ..pdf_generator import DICAnalysisPDFGenerator
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..models import DICAnalysis

class PdfGenerateMixin:
    """Миксин для генерации PDF отчетов DIC."""
    def pdf_generate(self, request, pk=None):
        """Генерирует и возвращает PDF отчет анализа."""
        instance = self.get_object()
        
        if instance.status !=DICAnalysis.Status.COMPLETED:
            return Response(
                {'eror': 'отчет может быть сгенирирован только для завершенного анализа'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pdf_generator = DICAnalysisPDFGenerator()
            pdf_buffer = pdf_generator.generate_report(instance)
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="dic_report_{instance.id}.pdf"'
            return response
        
        except Exception as e:
            return Response(
                {'error': f'Ошибка при генерации PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

