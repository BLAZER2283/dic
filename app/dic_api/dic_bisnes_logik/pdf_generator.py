from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO


class DICAnalysisPDFGenerator:
    """Генератор PDF отчетов для DIC анализа."""

    def __init__(self):
        pass
        
    def generate_report(self, analysis):
        """Генерирует PDF отчет для завершенного анализа."""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 50*mm, "DIC ANALYSIS REPORT")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 80*mm, "Sample Information:")
        
        c.setFont("Helvetica", 12)
        y_pos = height - 100*mm
        
        sample_info = [
            f"Sample Name: {getattr(analysis, 'sample_name', 'Not specified')}",
            f"Material: {getattr(analysis, 'material', 'Not specified')}",
            f"Manufacturer: {getattr(analysis, 'manufacturer', 'Not specified')}",
            f"Test Date: {getattr(analysis, 'test_date', None).strftime('%d.%m.%Y') if getattr(analysis, 'test_date', None) else 'Not specified'}"
        ]
        
        for info in sample_info:
            c.drawString(70, y_pos, info)
            y_pos -= 15
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos - 20, "Analysis Parameters:")
        
        c.setFont("Helvetica", 12)
        y_pos -= 40
        
        analysis_info = [
            f"Analysis Name: {analysis.name}",
            f"Task ID: {analysis.id}",
            f"Created: {analysis.created_at.strftime('%d.%m.%Y %H:%M')}",
            f"Completed: {analysis.completed_at.strftime('%d.%m.%Y %H:%M') if analysis.completed_at else 'Not completed'}",
            f"Window Size: {analysis.subset_size} px",
            f"Step Size: {analysis.step} px",
            f"Max Iterations: {analysis.max_iter}",
            f"Min Correlation: {analysis.min_correlation}"
        ]
        
        for info in analysis_info:
            c.drawString(70, y_pos, info)
            y_pos -= 15
        
        if analysis.status == analysis.Status.COMPLETED and y_pos > 150:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_pos - 20, "Displacement Analysis Results:")
            
            c.setFont("Helvetica", 12)
            y_pos -= 40
            
            results_info = [
                f"Mean Displacement: {analysis.mean_displacement:.4f} px" if analysis.mean_displacement is not None else "Mean Displacement: N/A",
                f"Max Displacement: {analysis.max_displacement:.4f} px" if analysis.max_displacement is not None else "Max Displacement: N/A",
                f"Median Displacement: {analysis.median_displacement:.4f} px" if analysis.median_displacement is not None else "Median Displacement: N/A",
                f"Std Deviation: {analysis.std_displacement:.4f} px" if analysis.std_displacement is not None else "Std Deviation: N/A",
                f"Correlation Quality: {analysis.correlation_quality:.2%}" if analysis.correlation_quality is not None else "Correlation Quality: N/A",
                f"Reliable Points: {analysis.reliable_points_percentage:.1f}%" if analysis.reliable_points_percentage is not None else "Reliable Points: N/A",
                f"Processing Time: {analysis.processing_time:.2f} sec" if analysis.processing_time is not None else "Processing Time: N/A"
            ]
            
            for info in results_info:
                if y_pos > 100:
                    c.drawString(70, y_pos, info)
                    y_pos -= 15
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_pos - 30, "CONCLUSION:")
            
            c.setFont("Helvetica", 12)
            conclusion_text = self._generate_conclusion(analysis)
            lines = conclusion_text.split('\n')
            y_pos -= 50
            
            for line in lines:
                if line.strip():
                    if y_pos < 50:
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y_pos = height - 50*mm
                    
                    c.drawString(70, y_pos, line)
                    y_pos -= 12
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _generate_conclusion(self, analysis):
        if analysis.status != analysis.Status.COMPLETED:
            return "Analysis not completed successfully."
        
        conclusion = "Based on the digital correlation analysis of images (DIC) "
        
        if getattr(analysis, 'sample_name', None):
            conclusion += f"of sample '{analysis.sample_name}' "
        else:
            conclusion += "of the provided sample "
            
        conclusion += "the following results were obtained:\n\n"
        
        if analysis.max_displacement is not None:
            conclusion += f"• The maximum measured displacement was {analysis.max_displacement:.4f} pixels\n"
        
        if analysis.mean_displacement is not None:
            conclusion += f"• The average displacement across all analysis points was {analysis.mean_displacement:.4f} pixels\n"
        
        if analysis.reliable_points_percentage is not None:
            conclusion += f"• Percentage of reliable correlation points: {analysis.reliable_points_percentage:.1f}%\n"
        
        if analysis.correlation_quality is not None:
            quality_desc = "high" if analysis.correlation_quality > 0.8 else "satisfactory" if analysis.correlation_quality > 0.6 else "low"
            conclusion += f"• Correlation quality: {quality_desc} ({analysis.correlation_quality:.2%})\n"
        
        conclusion += "\nThe analysis was performed with the following parameters:\n"
        conclusion += f"• Correlation window size: {analysis.subset_size} pixels\n"
        conclusion += f"• Analysis grid step: {analysis.step} pixels\n"
        conclusion += f"• Max number of iterations: {analysis.max_iter}\n"
        
        if analysis.processing_time is not None:
            conclusion += f"• Analysis execution time: {analysis.processing_time:.2f} seconds\n"
        
        conclusion += "\nIt is recommended to consider the obtained data when interpreting the mechanical properties of the material."
        
        return conclusion