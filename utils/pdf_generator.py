from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

def generate_pdf_report(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("政策文件分析报告", styles['Title']))
    elements.append(Spacer(1, 24))

    for idx, item in enumerate(results, 1):
        elements.append(Paragraph(f"问题 {idx}：{item['question']}", styles['Heading2']))
        elements.append(Paragraph(f"回答：{item['result']}", styles['Normal']))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes