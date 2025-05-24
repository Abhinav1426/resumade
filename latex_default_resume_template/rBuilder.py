from flask import Flask, send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# —— Register only the fonts you have ——
pdfmetrics.registerFont(TTFont('CMR10',  'cmunrm.ttf'))   # Roman
pdfmetrics.registerFont(TTFont('CMB10',  'cmunbx.ttf'))   # Bold
pdfmetrics.registerFont(TTFont('CMIT10', 'cmunti.ttf'))   # Italic

app = Flask(__name__)


def build_pdf(buffer):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()

    # —— Body text ——
    styles['BodyText'].fontName   = 'CMR10'
    styles['BodyText'].fontSize   = 10
    styles['BodyText'].leading    = 12
    styles['BodyText'].spaceAfter = 4

    # —— Name ——
    styles.add(ParagraphStyle(
        name='Name',
        fontName='CMB10',
        fontSize=20.74,
        leading=,
        alignment=1,
        spaceAfter=6
    ))

    # —— Contact line ——
    styles.add(ParagraphStyle(
        name='HeaderInfo',
        fontName='CMR10',
        fontSize=10,
        leading=12,
        alignment=1,
        spaceAfter=12
    ))

    # —— Section heading (bold, uppercase) ——
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='CMB10',
        fontSize=14,
        leading=16,
        spaceBefore=5,
        spaceAfter=4,
        alignment=0,
        uppercase=True
    ))

    # —— Subheadings ——
    styles.add(ParagraphStyle(
        name='SubHeading',
        fontName='CMB10',
        fontSize=12,
        leading=14,
        spaceBefore=6,
        spaceAfter=2
    ))

    # —— Education table styles ——
    styles.add(ParagraphStyle(
        name='EduInst',
        fontName='CMB10',
        fontSize=11,
        leading=11,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='EduDegree',
        fontName='CMIT10',
        fontSize=9,
        leading=9,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='EduDate',
        fontName='CMB10',
        fontSize=11,
        leading=11,
        alignment=2  # right
    ))
    styles.add(ParagraphStyle(
        name='EduLoc',
        fontName='CMIT10',
        fontSize=9,
        leading=9,
        alignment=2,  # right
        spaceAfter=1
    ))

    story = []

    # —— Header ——
    story.append(Paragraph('BUSHA VAISHNAV', styles['Name']))
    story.append(Paragraph(
        '+1 940-629-4438 · '
        '<a href="mailto:vaishnavbusha@gmail.com">'
          '<font color="blue">vaishnavbusha@gmail.com</font>'
        '</a> · '
        '<a href="https://linkedin.com/in/vaishnavbusha/">'
          '<font color="blue">linkedin.com/in/vaishnavbusha/</font>'
        '</a>',
        styles['HeaderInfo']
    ))

    # —— Education ——
    story.append(Paragraph('Education', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    # story.append(Spacer(1, 0))

    edu_data = [
        (
            'University of North Texas, Denton',
            'Masters in Data Science, GPA 4.0/4.0',
            'August 2024 – May 2026',
            'Denton, Texas'
        ),
        (
            'Anurag Group of Institutions (now Anurag University)',
            "Bachelor’s Degree (B.Tech) in Computer Science and Engineering, GPA 8.8/10",
            'July 2018 – August 2022',
            'Hyderabad, Telangana'
        )
    ]
    # Compute 2:1 column widths
    page_w, _ = letter
    usable_w = page_w - doc.leftMargin - doc.rightMargin
    left_col = usable_w * 1.93 / 3
    right_col = usable_w * 1 / 3
    for inst, degree, dates, loc in edu_data:
        table_data = [
            [ Paragraph(inst,   styles['EduInst']),
              Paragraph(dates,  styles['EduDate']) ],
            [ Paragraph(degree, styles['EduDegree']),
              Paragraph(loc,    styles['EduLoc'])  ]
        ]
        tbl = Table(table_data,colWidths=[left_col, right_col],)
        tbl.setStyle(TableStyle([
            ('VALIGN',      (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING',(0,0), (-1,-1), 0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 1.5))

    # —— Experience ——
    story.append(Paragraph('Experience', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    story.append(Spacer(1, 1))

    experiences = [
        {
            'title': 'Acintyo Tech Innovations Pvt. Ltd.',
            'designation': 'Software Engineer',
            'span': 'Dec 2023 – Jun 2024',
            'bullets': [
                'Developed healthcare-based B2B2C e-commerce Flutter app connecting retailers, consumers, and wholesalers.',
                'Built medical-consultation app with diagnostics, doctor calls, and prescription fulfillment.',
                'Shipped iOS & Android versions in parallel, cutting dev time substantially.'
            ]
        },
        {
            'title': 'Acintyo Tech Innovations Pvt. Ltd.',
            'designation': 'Software Engineer',
            'span': 'Dec 2023 – Jun 2024',
            'bullets': [
                'Developed healthcare-based B2B2C e-commerce Flutter app connecting retailers, consumers, and wholesalers.',
                'Built medical-consultation app with diagnostics, doctor calls, and prescription fulfillment.',
                'Shipped iOS & Android versions in parallel, cutting dev time substantially.'
            ]
        },
    ]
    for e in experiences:
        story.append(Paragraph(e['title'], styles['SubHeading']))
        items = [ListItem(Paragraph(b, styles['BodyText']), leftIndent=12)
                 for b in e['bullets']]
        story.append(ListFlowable(items, bulletType='bullet', bulletFontSize=6))
        story.append(Spacer(1, 6))


    doc.build(story)

@app.route('/resume')
def resume():
    buf = io.BytesIO()
    build_pdf(buf)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=False,
        download_name='Vaishnav_Busha_Resume.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
