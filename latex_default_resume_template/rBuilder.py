from flask import Flask, send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, Spacer
)
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Table, TableStyle

# —— Register only the fonts you have ——
pdfmetrics.registerFont(TTFont('CMR10',  'cmunrm.ttf'))   # Roman
pdfmetrics.registerFont(TTFont('CMB10',  'cmunbx.ttf'))   # Bold
pdfmetrics.registerFont(TTFont('CMIT10', 'cmunti.ttf'))   # Italic
pdfmetrics.registerFont(
    TTFont('BodoniMT', 'bodoni-mt-regular.ttf')
)
app = Flask(__name__)


def calculateTableColumnSplit(doc):
    # Compute 2:1 column widths
    page_w, _ = letter
    usable_w = page_w - doc.leftMargin - doc.rightMargin
    left_col = usable_w * 1.94 / 3
    right_col = usable_w * 1 / 3
    return left_col, right_col

def resumeStyling():
    large = 12
    small = 11
    xSmall = 10
    huge = 20.74
    styles = getSampleStyleSheet()
    # —— Body text ——
    styles['BodyText'].fontName = 'CMR10'
    styles['BodyText'].fontSize = xSmall
    styles['BodyText'].leading = small
    styles['BodyText'].spaceAfter = 0
    styles['BodyText'].alignment = TA_JUSTIFY

    # —— Name ——
    styles.add(ParagraphStyle(
        name='Name',
        fontName='BodoniMT',
        fontSize=huge,
        leading=10,
        alignment=1,
        spaceAfter=18,
    ))

    # —— Contact line ——
    styles.add(ParagraphStyle(
        name='HeaderInfo',
        fontName='CMR10',
        fontSize=xSmall,
        leading=12,
        alignment=1,
        spaceAfter=12
    ))

    # —— Section heading (bold, uppercase) ——
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='CMB10',
        fontSize=large,
        leading=large,

        spaceAfter=5,
        alignment=0,
        uppercase=True
    ))

    # —— Education table styles ——
    styles.add(ParagraphStyle(
        name='EduInst',
        fontName='CMB10',
        fontSize=small,
        leading=8,
    ))
    styles.add(ParagraphStyle(
        name='EduDegree',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=small,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='EduDate',
        fontName='CMB10',
        fontSize=small,
        leading=8,
        alignment=2  # right
    ))
    styles.add(ParagraphStyle(
        name='EduLoc',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=9,
        alignment=2,  # right
        spaceAfter=1
    ))

    # —— Experience table styles ——
    styles.add(ParagraphStyle(
        name='ExpTitle',
        fontName='CMB10',
        fontSize=small,
        leading=8,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExpRole',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=8,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExpDate',
        fontName='CMB10',
        fontSize=small,
        leading=8,
        alignment=2,  # right
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExpLoc',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=8,
        alignment=2,  # right
        spaceAfter=0
    ))

    # —— Extracurricular / Achievements styles ——
    styles.add(ParagraphStyle(
        name='ExtraTitle',
        fontName='CMB10',
        fontSize=small,
        leading=xSmall,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExtraDesc',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=xSmall,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExtraDate',
        fontName='CMB10',
        fontSize=small,
        leading=xSmall,
        alignment=2,  # right
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='ExtraLoc',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=xSmall,
        alignment=2,  # right
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='skill',
        fontName='CMR10',
        fontSize=xSmall,
        leading=small,
        spaceBefore=2,

        spaceAfter=0,
    ))
    return styles


from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, TableStyle

# 1) Make sure your 'Name' style is left-aligned:



def personalInformationBlock(story, styles):
    # — Name —
    story.append(Paragraph('BUSHA VAISHNAV', styles['Name']))

    # define a 4-space separator
    SEP = '&nbsp;&nbsp;&nbsp;&nbsp;'

    contact_html = SEP.join([
        # phone
        '<img src="phone.png" width="10" height="10"/>'
        '&nbsp;+91-8919707712',
        # email
        '<img src="mail.png" width="10" height="10"/>'
        '&nbsp;<a href="mailto:mpabhinav1426@gmail.com">'
          '<font color="blue">mpabhinav1426@gmail.com</font>'
        '</a>',
        # linkedin
        '<img src="linkedin.png" width="10" height="10"/>'
        '&nbsp;<a href="https://www.linkedin.com/in/abhinav1426/">'
          '<font color="blue">linkedin.com/in/abhinav1426/</font>'
        '</a>'
    ])

    story.append(Paragraph(contact_html, styles['HeaderInfo']))
    # — your spaced name as before —
    # story.append(Paragraph('BUSHA VAISHNAV', styles['Name']))
    # # — Name (now flush left) —
    # story.append(Paragraph('BUSHA VAISHNAV', styles['Name']))
    #
    # # — Three icon+text pairs —
    # items = [
    #     ('phone.png', '+91-8919707712', None),
    #     ('mail.png', 'mpabhinav1426@gmail.com', 'mailto:mpabhinav1426@gmail.com'),
    #     ('linkedin.png', 'linkedin.com/in/abhinav1426/', 'https://www.linkedin.com/in/abhinav1426/'),
    # ]
    #
    # # Build each inner 1×2 (icon + text)
    # inners = []
    # for icon_file, text, href in items:
    #     icon = Image(icon_file, width=10, height=10)
    #     txt = f'<a href="{href}"><font color="blue">{text}</font></a>' if href else text
    #     para = Paragraph(txt, styles['HeaderInfo'])
    #
    #     inner = Table([[icon, para]], colWidths=[10, None])
    #     inner.setStyle(TableStyle([
    #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #         ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
    #         ('ALIGN', (1, 0), (1, 0), 'LEFT'),
    #         ('RIGHTPADDING', (0, 0), (0, 0), 2),  # 2pt gap icon→text
    #         ('LEFTPADDING', (0, 0), (-1, -1), 0),
    #         ('TOPPADDING', (0, 0), (-1, -1), 0),
    #         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    #     ]))
    #     inners.append(inner)
    #
    # # Compute each outer cell = 1/3 page width (minus ½" margins)
    # page_w = letter[0]
    # usable_w = page_w - 2 * (0.5 * inch)
    # third_width = usable_w / 3
    #
    # # 2) Outer table flush-left, with all cells left-aligned
    # outer = Table([inners],
    #               colWidths=[third_width] * 3,
    #               hAlign='LEFT')
    # outer.setStyle(TableStyle([
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # everything left
    #     ('LEFTPADDING', (0, 0), (-1, -1), 0),
    #     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    #     ('TOPPADDING', (0, 0), (-1, -1), 0),
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    # ]))
    #
    # story.append(outer)


def education(story,styles,doc):
    # —— Education ——
    story.append(Paragraph('Education', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

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
    left_col,right_col = calculateTableColumnSplit(doc)
    for inst, degree, dates, loc in edu_data:
        table_data = [
            [Paragraph(inst, styles['EduInst']),
             Paragraph(dates, styles['EduDate'])],
            [Paragraph(degree, styles['EduDegree']),
             Paragraph(loc, styles['EduLoc'])]
        ]
        tbl = Table(table_data, colWidths=[left_col, right_col], )
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 1.6))
    story.append(Spacer(1, 2.4,))
def experiences(story,styles,doc):

    # —— Experience ——
    story.append(Paragraph('Experience', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    # ensure you have left_col/right_col already calculated above
    experiences = [
        {
            'title': 'Acintyo Tech Innovations Pvt. Ltd.',
            'designation': 'Software Engineer',
            'span': 'December 2023 – June 2024',
            'location': 'Hyderabad, India',
            'bullets': [
                'As a flutter developer, developed healthcare based eCommerce B2B2C app. This app enables retailers in selling their goods to consumers and also to buy products from well-known wholesalers such as Acintyo.',
                'Responsible for developing an app for medical consultations…',
                'Mitigated resources … by developing both iOS and Android apps…'
            ]
        },
        {
            'title': 'Acintyo Tech Innovations Pvt. Ltd.',
            'designation': 'Software Engineer',
            'span': 'December 2023 – June 2024',
            'location': 'Hyderabad, India',
            'bullets': [
                'As a flutter developer, developed healthcare based eCommerce B2B2C app. This app enables retailers in selling their goods to consumers and also to buy products from well-known wholesalers such as Acintyo.',
                'Responsible for developing an app for medical consultations…',
                'Mitigated resources … by developing both iOS and Android apps…'
            ]
        },
        # add more entries as needed…
        ]
    left_col, right_col = calculateTableColumnSplit(doc)
    for e in experiences:
        # 2×2 header table
        tbl = Table([
            [Paragraph(e['title'], styles['ExpTitle']),
             Paragraph(e['span'], styles['ExpDate'])],
            [Paragraph(e['designation'], styles['ExpRole']),
             Paragraph(e['location'], styles['ExpLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(tbl)


        # — bullet list with custom indent & tighter bullet‐text gap —
        items = []
        for b in e['bullets']:
            items.append(
                ListItem(
                    Paragraph(b, styles['BodyText'],),
                    leftIndent=20,  # indent bullet+text from the page margin
                    bulletIndent=0,  # bullet sits exactly at leftIndent
                )

            )

        story.append(
            ListFlowable(
                items,
                bulletType='bullet',
                bulletFontName='CMR10',
                bulletFontSize=8,
                bulletOffsetY=-1,
                leftIndent=10,  # extra indent from the page margin

            )
        )
        # original spacer
        story.append(Spacer(1, 5,))
    story.append(Spacer(1, 5, ))

def skills(story,styles):
    # —— Technical Skills ——
    story.append(Paragraph('Technical Skills', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    skills = [
        {
            'skillName': 'Languages',
            'list': ['Dart, Java, Javascript, C, Python, C#, SQL, HTML, CSS'],
        },
        {
            'skillName': 'Frameworks',
            'list': ['Flutter, Firebase, NodeJS, Spring, Spring Boot, Spring MVC, Maven, RESTful APIs'],
        },
        {
            'skillName': 'Developer Tools',
            'list': ['PostMan, Maven, Docker, Kubernetes,'
                     ' VS Code IDE, MS Office, Eclipse IDE'],
        },
        {
            'skillName': 'Softwares Known',
            'list': ['Adobe Illustrator, Adobe Photoshop, Adobe XD, MS Office'],
        },
    ]

    for skill in skills:
        name = skill['skillName']
        desc = ' '.join(skill['list'])
        # use <font name="CMB10"> to switch to your bold font
        story.append(
            Paragraph(
                f'<font name="CMB10">{name}:</font> {desc}',
                styles['skill']
            )
        )
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 5))

def extras(story,styles,doc):
    # —— Extracurricular / Achievements section ——
    story.append(Paragraph('Extracurricular / Achievements', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    extras = [
        {
            'title': 'Winners of Major League Hack Hackathon',
            'desc': "Won first prize in Microsoft’s MLH Hackathon for developing a chatbot on choking health issue.",
            'date': 'December 2019',
            'loc': 'A.G.I., Telangana'
        },
        {
            'title': 'Participated in ICACII',
            'desc': 'Event Manager for machine learning workshop conducted at Intelligence and Informatics.',
            'date': 'January 2019',
            'loc': 'A.G.I., Telangana'
        },
        {
            'title': 'Participated in IMO',
            'desc': 'Secured a gold medal in International Maths Olympiad.',
            'date': 'December 2012',
            'loc': 'R.B.S., Hyderabad'
        },
        {
            'title': 'National Space Society Space Settlement Contest by NASA',
            'desc': "Designed and developed a habitable space station virtually named 'ATOLL'.",
            'date': 'March 2015',
            'loc': 'R.B.S., Hyderabad'
        },
    ]
    left_col, right_col = calculateTableColumnSplit(doc)
    # reuse left_col/right_col from earlier (2:1 ratio)
    for ex in extras:
        tbl = Table([
            [Paragraph(ex['title'], styles['ExtraTitle']),
             Paragraph(ex['date'], styles['ExtraDate'])],
            [Paragraph(ex['desc'], styles['ExtraDesc']),
             Paragraph(ex['loc'], styles['ExtraLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 5))

def projects(story,styles,doc):
    # —— Projects ——
    story.append(Paragraph('Projects', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    # your list of project dicts
    projects = [
        {
            'projectName': 'Calculator',
            'projectCaption': 'Personal Production Application',
            'start': 'June 2020',
            'end': 'August 2020',
            'location': 'Hyderabad, India',
            'projectDetails': [
                'By using flutter and provider as state management, developed a three-themed neumorphic calculator. The application has garnered over 50,000+ downloads worldwide on Playstore.'
            ],
            'externalSources': [
                {'name': 'PlayStore',
                 'link': 'https://play.google.com/store/apps/details?id=com.aquelastudios.calculater'},
                {'name': 'GitHub', 'link': 'https://github.com/vaishnavbusha/neucalc'},
            ]
        },
        {
            'projectName': 'GymTracker',
            'projectCaption': 'Personal Production Application',
            'start': 'September 2023',
            'end': 'Present',
            'location': 'Hyderabad, India',
            'projectDetails': [
                'Designed and developed a B2B gym-management app: RSA-encrypted QR check-ins, exercise stats; Spring Boot + Firebase + AWS backend.',
                'Integrated admin companion app for Firestore & RTDB operations.'
            ],
            'externalSources': [
                {'name': 'PlayStore',
                 'link': 'https://play.google.com/store/apps/details?id=com.aquelastudios.gymtracker'},
                {'name': 'GitHub', 'link': 'https://github.com/vaishnavbusha/gymtracker'},
            ]
        },
        # …add more projects here…
    ]
    left_col, right_col = calculateTableColumnSplit(doc)
    for p in projects:
        # two-column header: project name & dates / caption & location
        tbl = Table([
            [Paragraph(p['projectName'], styles['EduInst']),
             Paragraph(f"{p['start']} – {p['end']}", styles['EduDate'])],
            [Paragraph(p['projectCaption'], styles['EduDegree']),
             Paragraph(p['location'], styles['EduLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(tbl)

        # bullets for project details
        items = []
        for detail in p['projectDetails']:
            items.append(
                ListItem(
                    Paragraph(detail, styles['BodyText']),
                    leftIndent=18,
                    bulletIndent=0,
                    bulletFontName='CMR10',
                    bulletFontSize=8,
                    bulletOffsetY=-1,
                    rightIndent=0
                )
            )
        story.append(
            ListFlowable(
                items,
                bulletType='bullet',
                leftIndent=10,
                valueIndent=10,
                spaceBefore=4,  # ← new
                spaceAfter=0  # ← new

            )
        )

        links = [
            f'<a href="{src["link"]}"><font color="blue">{src["name"]}</font></a>'
            for src in p['externalSources']
        ]
        link_text = f'<font name="CMB10">Link(s):</font> ' + ', '.join(links)

        # make it a ListItem…
        link_item = ListItem(
            Paragraph(link_text, styles['BodyText']),
            leftIndent=18,  # indent bullet + text
            bulletIndent=0  # bullet sits exactly at leftIndent
        )

        # …and put it in a ListFlowable
        story.append(
            ListFlowable(
                [link_item],
                bulletType='bullet',
                bulletFontName='CMR10',
                bulletFontSize=8,
                bulletOffsetY=-1,
                leftIndent=10,  # extra margin from page edge
                # spaceBefore=4,  # ← new
                # spaceAfter=0
            )
        )

        # then maybe a small Spacer before next section
        story.append(Spacer(1, 5))


    story.append(Spacer(1, 5))

def build_pdf(buffer):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch
    )


    styles = resumeStyling()
    story = []
    personalInformationBlock(story,styles)
    education(story,styles,doc)
    experiences(story,styles,doc)
    skills(story,styles)
    projects(story,styles,doc)
    extras(story,styles,doc)

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
