from rest_framework.decorators import action
from .pdf_generator import DICAnalysisPDFGenerator
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..models import AnalysisTask


class PdfGenerateMixin:
    """Mixin for generating DIC PDF reports."""

    @action(detail=True, methods=['get'])
    def pdf_generate(self, request, pk=None):
        """Generate and return DIC analysis PDF report."""
        instance = self.get_object()

        if instance.status != AnalysisTask.Status.COMPLETED:
            return Response(
                {'error': 'Report can only be generated for completed analysis'},
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
                {'error': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
