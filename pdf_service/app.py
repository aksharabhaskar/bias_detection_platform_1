from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import os
from datetime import datetime
from typing import Dict, Any, List
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def create_bar_chart(data: Dict[str, float], title: str, ylabel: str = "Rate") -> io.BytesIO:
    """Create a bar chart and return as BytesIO"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    groups = list(data.keys())
    values = list(data.values())
    
    ax.bar(groups, values, color='steelblue', alpha=0.7)
    ax.set_xlabel('Group', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save to BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_scatter_chart(data: Dict[str, Dict[str, float]], title: str) -> io.BytesIO:
    """Create a scatter plot for equalized odds"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    for group, values in data.items():
        ax.scatter(values.get('fpr', 0), values.get('tpr', 0), 
                  s=100, alpha=0.7, label=group)
    
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_heatmap_chart(data: Dict[str, List[float]], bins: List[str] | None, title: str) -> io.BytesIO:
    """Create a heatmap for calibration by group"""
    if not data:
        return io.BytesIO()

    groups = list(data.keys())
    first_group_values = data[groups[0]] if data[groups[0]] else []
    bin_labels = bins if bins else [f"Bin {i+1}" for i in range(len(first_group_values))]

    matrix = []
    for group in groups:
        values = data[group]
        row = []
        for idx in range(len(bin_labels)):
            value = values[idx] if idx < len(values) else 0
            row.append(value)
        matrix.append(row)

    matrix_np = np.array(matrix)

    fig, ax = plt.subplots(figsize=(8, 5))
    cax = ax.imshow(matrix_np, aspect='auto', cmap='Blues')

    ax.set_xticks(range(len(bin_labels)))
    ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels(groups, fontsize=10)
    ax.set_title(title, fontsize=14, fontweight='bold')

    for i in range(len(groups)):
        for j in range(len(bin_labels)):
            ax.text(j, i, f"{matrix_np[i, j]:.2f}", ha='center', va='center', color='black', fontsize=7)

    fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, label='Actual shortlisting rate')
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    return img_buffer

def generate_pdf_report(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate comprehensive PDF report with all fairness metrics
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        alignment=TA_JUSTIFY
    )
    
    # Title
    elements.append(Paragraph("AI Fairness Audit Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary = data.get('summary', {})
    summary_text = f"""
    This report presents a comprehensive fairness audit of the AI system analyzing {data.get('dataset_name', 'the dataset')}. 
    The analysis evaluated {summary.get('total_metrics', 0)} fairness metrics across the protected attribute: <b>{data.get('protected_attr', 'N/A')}</b>.
    <br/><br/>
    <b>Overall Assessment:</b> {summary.get('overall_assessment', 'Unknown')}<br/>
    <b>Fair Metrics:</b> {summary.get('fair', 0)} | <b>Warnings:</b> {summary.get('warning', 0)} | <b>Violations:</b> {summary.get('violation', 0)}
    """
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Dataset Information
    elements.append(Paragraph("Dataset Information", heading_style))
    dataset_info = [
        ['Property', 'Value'],
        ['Filename', data.get('dataset_name', 'N/A')],
        ['Rows', str(data.get('rows', 'N/A'))],
        ['Columns', str(data.get('columns', 'N/A'))],
        ['Upload Date', data.get('upload_date', 'N/A')],
        ['Protected Attribute', data.get('protected_attr', 'N/A')],
        ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    dataset_table = Table(dataset_info, colWidths=[2*inch, 4*inch])
    dataset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(dataset_table)
    elements.append(PageBreak())
    
    # Metrics Details
    elements.append(Paragraph("Detailed Fairness Metrics Analysis", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    metrics = data.get('metrics', [])
    
    for i, metric in enumerate(metrics):
        # Metric name and assessment
        metric_name = metric.get('metric_name', 'Unknown')
        display_name = metric.get('explanation', {}).get('display_name', metric_name.replace('_', ' ').title())
        assessment = metric.get('fairness_assessment', 'Unknown')
        
        # Color code assessment
        assessment_color = colors.green if assessment == 'Fair' else colors.orange if assessment == 'Warning' else colors.red
        
        elements.append(Paragraph(f"{i+1}. {display_name}", subheading_style))
        
        # Assessment badge
        assessment_text = f"<font color='{assessment_color.hexval()}'>● {assessment}</font>"
        elements.append(Paragraph(assessment_text, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Definition
        definition = metric.get('explanation', {}).get('definition', 'No definition available')
        elements.append(Paragraph(f"<b>Definition:</b> {definition}", body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # What this means
        explanation_data = metric.get('explanation', {})
        what_means = explanation_data.get('what_this_means', '')
        if what_means:
            elements.append(Paragraph(f"<b>What This Means:</b> {what_means}", body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # What is wrong
        what_wrong = explanation_data.get('what_is_wrong', '')
        if what_wrong:
            elements.append(Paragraph(f"<b>What Is Wrong:</b> {what_wrong}", body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Root causes
        root_causes = explanation_data.get('root_causes', [])
        if root_causes:
            causes_text = "<b>Likely Root Causes:</b><br/>"
            for cause in root_causes:
                causes_text += f"&nbsp;&nbsp;• {cause}<br/>"
            elements.append(Paragraph(causes_text, body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Recruiter actions
        actions = explanation_data.get('recruiter_actions', [])
        if actions:
            actions_text = "<b>Recommended Actions:</b><br/>"
            for action in actions:
                actions_text += f"&nbsp;&nbsp;✓ {action}<br/>"
            elements.append(Paragraph(actions_text, body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Dashboard recommendation
        recommendation = explanation_data.get('dashboard_recommendation', '')
        if recommendation:
            elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Values
        values = metric.get('values', {})
        if isinstance(values, dict) and values:
            values_text = "<b>Calculated Values:</b><br/>"
            for group, value in values.items():
                if isinstance(value, (int, float)):
                    values_text += f"&nbsp;&nbsp;• {group}: {value:.4f}<br/>"
                elif isinstance(value, dict):
                    values_text += f"&nbsp;&nbsp;• {group}: {value}<br/>"
            elements.append(Paragraph(values_text, body_style))
        elif isinstance(values, (int, float)):
            elements.append(Paragraph(f"<b>Value:</b> {values:.4f}", body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Visualization (if applicable)
        viz_data = metric.get('visualization_data', {})
        viz_type = viz_data.get('visualization_type')
        
        if viz_type == 'bar' and isinstance(values, dict):
            try:
                chart_buffer = create_bar_chart(
                    {k: float(v) if isinstance(v, (int, float)) else float(v.get('rate', 0)) 
                     for k, v in values.items() if isinstance(v, (int, float, dict))},
                    display_name,
                    "Rate"
                )
                img = Image(chart_buffer, width=5*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.1*inch))
            except Exception as e:
                print(f"Error creating chart: {e}")
        
        elif viz_type == 'scatter' and isinstance(values, dict):
            try:
                chart_buffer = create_scatter_chart(values, display_name)
                img = Image(chart_buffer, width=5*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.1*inch))
            except Exception as e:
                print(f"Error creating scatter plot: {e}")
        elif viz_type == 'heatmap' and isinstance(values, dict):
            try:
                chart_buffer = create_heatmap_chart(values, viz_data.get('bins'), display_name)
                img = Image(chart_buffer, width=5*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.1*inch))
            except Exception as e:
                print(f"Error creating heatmap: {e}")
        
        # Interpretation
        interpretation = metric.get('explanation', {}).get('interpretation', '')
        if interpretation:
            elements.append(Paragraph(f"<b>Interpretation:</b> {interpretation}", body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Recommendations
        recommendations = metric.get('explanation', {}).get('recommendations', '')
        if recommendations and assessment != 'Fair':
            elements.append(Paragraph(f"<b>Recommendations:</b> {recommendations}", body_style))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Page break every 3 metrics
        if (i + 1) % 3 == 0 and i < len(metrics) - 1:
            elements.append(PageBreak())
    
    # Final Recommendations
    elements.append(PageBreak())
    elements.append(Paragraph("Summary and Recommendations", heading_style))
    
    violation_count = summary.get('violation', 0)
    warning_count = summary.get('warning', 0)
    
    if violation_count > 0:
        rec_text = f"""
        This audit identified <b>{violation_count} fairness violation(s)</b> and <b>{warning_count} warning(s)</b>. 
        Immediate action is recommended to address these issues before deployment or continued use of the AI system.
        <br/><br/>
        <b>Key Actions:</b><br/>
        1. Review all metrics marked as violations in detail<br/>
        2. Investigate root causes in training data and model architecture<br/>
        3. Implement recommended mitigation strategies<br/>
        4. Re-evaluate after implementing changes<br/>
        5. Establish ongoing monitoring procedures
        """
    elif warning_count > 0:
        rec_text = f"""
        This audit identified <b>{warning_count} warning(s)</b>. While no severe violations were detected, 
        attention should be given to these areas to prevent potential fairness issues.
        <br/><br/>
        <b>Key Actions:</b><br/>
        1. Monitor warned metrics closely<br/>
        2. Consider preventive adjustments<br/>
        3. Establish regular fairness audits
        """
    else:
        rec_text = """
        Congratulations! This audit found no fairness violations or warnings. However, fairness is an ongoing concern.
        <br/><br/>
        <b>Key Actions:</b><br/>
        1. Maintain regular fairness monitoring<br/>
        2. Re-audit when data or model changes<br/>
        3. Stay informed about fairness best practices
        """
    
    elements.append(Paragraph(rec_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = """
    <br/><br/>
    <i>This report was generated by the AI Fairness Audit Dashboard. 
    For questions or concerns about this audit, please consult with your organization's 
    AI ethics and compliance team.</i>
    """
    elements.append(Paragraph(footer_text, body_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF report from analysis results
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(data)
        
        # Create filename
        dataset_name = data.get('dataset_name', 'dataset').replace(' ', '_')
        filename = f"fairness_audit_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'PDF Generation Service'})

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host=host, port=port, debug=True)
