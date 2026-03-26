from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.utils import timezone
import os


class DICAnalysisPDFGenerator:
    """PDF report generator for DIC analysis."""

    def generate_report(self, task):
        """
        Generate PDF report.

        Args:
            task: AnalysisTask object

        Returns:
            BytesIO buffer with PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20
        )
        elements.append(Paragraph("DIC Analysis Report", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # General Information
        elements.append(Paragraph("General Information", styles['Heading2']))
        info_data = [
            ["Task Name:", task.name],
            ["Task ID:", str(task.id)],
            ["Status:", task.get_status_display()],
            ["Created:", task.created_at.strftime("%d.%m.%Y %H:%M")],
            ["Completed:", task.completed_at.strftime("%d.%m.%Y %H:%M") if task.completed_at else "In Progress"],
            ["Processing Time:", f"{task.processing_time:.2f} sec." if task.processing_time else "N/A"],
        ]

        # Sample Information
        if hasattr(task, 'sample'):
            sample = task.sample
            info_data.extend([
                ["Sample:", sample.name],
                ["Material:", sample.material or "N/A"],
                ["Manufacturer:", sample.manufacture or "N/A"],
                ["Test Date:", sample.test_date.strftime("%d.%m.%Y") if sample.test_date else "N/A"],
            ])

        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))

        # Analysis Parameters
        if hasattr(task, 'parameters'):
            params = task.parameters
            elements.append(Paragraph("Analysis Parameters", styles['Heading2']))
            params_data = [
                ["Subset Size:", str(params.subset_size)],
                ["Step Size:", str(params.step)],
                ["Max Iterations:", str(params.max_iter)],
                ["Min Correlation:", str(params.min_correlation)],
            ]
            params_table = Table(params_data, colWidths=[2.5*inch, 3.5*inch])
            params_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(params_table)
            elements.append(Spacer(1, 0.3*inch))

        # Analysis Results
        if hasattr(task, 'results'):
            results = task.results
            elements.append(Paragraph("Analysis Results", styles['Heading2']))
            results_data = [
                ["Mean Displacement:", f"{results.mean_displacement:.4f}" if results.mean_displacement else "N/A"],
                ["Max Displacement:", f"{results.max_displacement:.4f}" if results.max_displacement else "N/A"],
                ["Median Displacement:", f"{results.median_displacement:.4f}" if results.median_displacement else "N/A"],
                ["Std Deviation:", f"{results.std_displacement:.4f}" if results.std_displacement else "N/A"],
                ["Correlation Quality:", f"{results.correlation_quality:.4f}" if results.correlation_quality else "N/A"],
                ["Reliable Points:", f"{results.reliable_points_percentage:.2f}%" if results.reliable_points_percentage else "N/A"],
            ]
            results_table = Table(results_data, colWidths=[2.5*inch, 3.5*inch])
            results_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(results_table)
            elements.append(Spacer(1, 0.3*inch))

        # Images
        if hasattr(task, 'images'):
            images = task.images
            elements.append(Paragraph("Images", styles['Heading2']))

            if images.displacement_map_path and os.path.exists(images.displacement_map_path):
                try:
                    img = Image(images.displacement_map_path, width=6*inch, height=4*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    elements.append(Paragraph(f"Error loading image: {e}", styles['Normal']))

        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=2,
            textColor=colors.grey
        )
        elements.append(Paragraph(f"Generated: {timezone.now().strftime('%d.%m.%Y %H:%M:%S')}", footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
