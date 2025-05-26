from flask import Flask, send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, Spacer
)
import json

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

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
        spaceAfter=16,
    ))
    # —— Name ——
    styles.add(ParagraphStyle(
        name='headerLoc',
        fontName='CMR10',
        fontSize=small,
        leading=10,
        alignment=TA_CENTER,
        spaceAfter=8,

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
        fontSize=xSmall,
        leading=8,
    ))
    styles.add(ParagraphStyle(
        name='EduDegree',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=8,
        spaceAfter=0
    ))
    styles.add(ParagraphStyle(
        name='EduDate',
        fontName='CMB10',
        fontSize=xSmall,
        leading=8,
        alignment=2  # right
    ))
    styles.add(ParagraphStyle(
        name='EduLoc',
        fontName='CMIT10',
        fontSize=xSmall,
        leading=8,
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
        leading=xSmall,


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

def render_personal_info(data, story, styles):
    """
    Renders:
     - name (required)
     - location (required)
     - phone, email (required)
     - socials (optional)
    """
    name = data.get('name', '').strip()
    location = data.get('location', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    if not (name and location and phone and email):
        return

    story.append(Paragraph(name, styles['Name']))
    story.append(Paragraph(location, styles['headerLoc']))
    SEP = '&nbsp;&nbsp;&nbsp;&nbsp;'
    parts = []



    # Phone
    parts.append(f'<img src="phone.png" width="10" height="10"/>&nbsp;{phone}')

    # Email
    parts.append(
        f'<img src="mail.png" width="10" height="10"/>&nbsp;'
        f'<a href="mailto:{email}"><u>{email}</u></a>'
    )

    # Optional socials
    for soc in data.get('socials', []):
        name = soc.get('name', '').strip()
        link = soc.get('link', '').strip()
        if not (name and link):
            continue
        icon = f'{name.lower()}.png'
        parts.append(
            f'<img src="{icon}" width="10" height="10"/>&nbsp;'
            f'<a href="{link}"><u>{name}</u></a>'
        )

    story.append(Paragraph(SEP.join(parts), styles['HeaderInfo']))


# def render_personal_info(data, story, styles):
#     # — Name —
#     story.append(Paragraph(data['name'], styles['Name']))
#     SEP = '&nbsp;&nbsp;&nbsp;&nbsp;'
#
#     parts = [
#         f'<img src="phone.png" width="10" height="10"/>&nbsp;{data["phone"]}',
#         f'<img src="mail.png" width="10" height="10"/>&nbsp;'
#         f'<a href="mailto:{data["email"]}"><u>{data["email"]}</u></a>',
#     ]
#
#     # add socials with icons, but only if link is non-empty
#     for soc in data.get('socials', []):
#         link = soc.get('link', '').strip()
#         if not link:
#             continue
#         icon = soc['name'].lower() + '.png'
#         parts.append(
#             f'<img src="{icon}" width="10" height="10"/>&nbsp;'
#             f'<a href="{link}"><u>{soc["name"]}</u></a>'
#         )
#
#     story.append(
#         Paragraph(SEP.join(parts), styles['HeaderInfo'])
#     )





def render_education_details(edus, story, styles, doc):
    """
    Renders each education entry if it has all required fields:
      institution, degree, location, start_date, gpa, gpa_out_off
    end_date is optional.
    """
    if not edus:
        return

    story.append(Paragraph('Education', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for ed in edus:
        inst = ed.get('institution', '').strip()
        deg = ed.get('degree', '').strip()
        loc = ed.get('location', '').strip()
        start = ed.get('start_date', '').strip()
        gpa = ed.get('gpa', '').strip()
        out_off = ed.get('gpa_out_off', '').strip()
        if not (inst and deg and loc and start and gpa and out_off):
            continue

        # Optional end date
        end = ed.get('end_date', '').strip()
        span = f"{start} – {end}" if end else start
        degree_text = f"{deg}, GPA {gpa}/{out_off}"

        tbl = Table([
            [Paragraph(inst, styles['EduInst']), Paragraph(span, styles['EduDate'])],
            [Paragraph(degree_text, styles['EduDegree']), Paragraph(loc, styles['EduLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))

        story.append(tbl)
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 5))
#
# def render_education_details(edus, story, styles, doc):
#     story.append(Paragraph('Education', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     left_col, right_col = calculateTableColumnSplit(doc)
#     for ed in edus:
#         degree = f"{ed['degree']}, GPA {ed['gpa']}/{ed['gpa_out_off']}"
#         span = f"{ed.get('start_date','')} – {ed['end_date']}"
#         tbl = Table([
#             [Paragraph(ed['institution'], styles['EduInst']),
#              Paragraph(span, styles['EduDate'])],
#             [Paragraph(degree, styles['EduDegree']),
#              Paragraph(ed['location'], styles['EduLoc'])]
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN',(0,0),(-1,-1),'TOP'),
#             ('LEFTPADDING',(0,0),(-1,-1),0),
#             ('RIGHTPADDING',(0,0),(-1,-1),0),
#         ]))
#         story.append(tbl)
#         story.append(Spacer(1, 5))
#     story.append(Spacer(1, 5, ))


def render_experiences_details(exps, story, styles, doc):
    """
    Renders each experience entry if it has:
      designation, companyName, location, start_date
    Optional: end_date, caption, points
    """
    if not exps:
        return

    story.append(Paragraph('Experience', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for e in exps:
        desig = e.get('designation','').strip()
        comp  = e.get('companyName','').strip()
        loc   = e.get('location','').strip()
        start = e.get('start_date','').strip()
        if not (desig and comp and loc and start):
            continue

        # Optional fields
        end     = e.get('end_date','').strip()
        caption = e.get('caption','').strip()
        points  = e.get('points', [])

        span = f"{start} – {end}" if end else start

        # Header: designation & date, company & location
        tbl = Table([
            [Paragraph(desig, styles['ExpTitle']), Paragraph(span, styles['ExpDate'])],
            [Paragraph(comp if not caption else caption, styles['ExpRole']),
             Paragraph(loc, styles['ExpLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(tbl)

        # Bullet points if present
        if points:
            items = [
                ListItem(Paragraph(pt, styles['BodyText']), leftIndent=18, bulletIndent=0)
                for pt in points
            ]
            story.append(
                ListFlowable(items,
                    bulletType='bullet', bulletFontName='CMR10',
                    bulletFontSize=8, bulletOffsetY=-1, leftIndent=10
                )
            )
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 5))

# def render_experiences_details(exps,story,styles,doc):
#     story.append(Paragraph('Experience', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     left_col, right_col = calculateTableColumnSplit(doc)
#     for e in exps:
#         span = f"{e['start_date']} – {e['end_date']}"
#         tbl = Table([
#             [Paragraph(e['companyName'], styles['ExpTitle']),
#              Paragraph(span, styles['ExpDate'])],
#             [Paragraph(e['designation'], styles['ExpRole']),
#              Paragraph(e['location'], styles['ExpLoc'])],
#
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING', (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ]))
#         story.append(tbl)
#
#         items = [
#             ListItem(Paragraph(pt, styles['BodyText']), leftIndent=20, bulletIndent=0)
#             for pt in e['points']
#         ]
#         story.append(
#             ListFlowable(items,
#                          bulletType='bullet',
#                          bulletFontName='CMR10',
#                          bulletFontSize=8,
#                          bulletOffsetY=-1,
#                          leftIndent=10,
#                          )
#         )
#         story.append(Spacer(1, 5))
#     story.append(Spacer(1, 5, ))


def render_skills_details(data, story, styles):
    """
    Renders each skill category if it has:
      name, data (non-empty list)
    """
    if not data:
        return

    story.append(Paragraph('Technical Skills', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    for sk in data:
        name = sk.get('name','').strip()
        items = sk.get('data', [])
        if not (name and items):
            continue

        skills_text = ', '.join(items)
        story.append(
            Paragraph(f'<font name="CMB10">{name}:</font> {skills_text}', styles['BodyText'])
        )
        # story.append(Spacer(1, 2))

    story.append(Spacer(1, 8))

# def render_skills_details(data,story,styles):
#     story.append(Paragraph('Technical Skills', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     for sk in data:
#         items = ', '.join(sk['data'])
#         story.append(
#             Paragraph(f'<font name="CMB10">{sk["name"]}:</font> {items}', styles['BodyText'])
#         )
#         story.append(Spacer(1, 2))
#     story.append(Spacer(1, 5))

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


def render_extras_details(data, story, styles, doc):
    """
    Renders each extracurricular/achievement if it has:
      name, type, location, date, description
    """
    if not data:
        return

    story.append(Paragraph('Extracurricular / Achievements', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for item in data:
        name = item.get('name','').strip()
        type_ = item.get('type','').strip()
        loc = item.get('location','').strip()
        date = item.get('date','').strip()
        desc = item.get('description','').strip()
        if not (name and type_ and loc and date and desc):
            continue


        tbl = Table([
            [Paragraph(name, styles['ExtraTitle']), Paragraph(date, styles['ExtraDate'])],
            [Paragraph(desc, styles['ExtraDesc']), Paragraph(loc, styles['ExtraLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 5))

# def render_extras_details(data,story,styles,doc):
#     # —— Extracurricular / Achievements section ——
#     if not data:
#         return
#
#     story.append(Paragraph('Extracurricular / Achievements', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#
#     left_col, right_col = calculateTableColumnSplit(doc)
#
#     for item in data:
#         # skip if no name/date
#         name = item.get('name', '').strip()
#         date = item.get('date', '').strip()
#         if not name or not date:
#             continue
#
#         desc = item.get('description', '').strip()
#
#         loc = item.get('location', '').strip()
#         # combine institution + location
#
#
#         tbl = Table([
#             [Paragraph(name, styles['ExtraTitle']),
#              Paragraph(date, styles['ExtraDate'])],
#             [Paragraph(desc, styles['ExtraDesc']),
#              Paragraph(loc, styles['ExtraLoc'])]
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING', (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ]))
#
#         story.append(tbl)
#         story.append(Spacer(1, 2))
#
#     # a little extra space at the end
#     story.append(Spacer(1, 5))

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
def render_projects_details(data, story, styles, doc):
    """
    Renders each project if it has:
      projectName, location, projectDetails (non-empty list)
    Optional: caption, start_date, end_date, url, externalSources, technologiesUsed
    """
    if not data:
        return

    story.append(Paragraph('Projects', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for p in data:
        name     = p.get('projectName','').strip()
        loc      = p.get('location','').strip()
        details  = p.get('projectDetails', [])
        if not (name and loc and details):
            continue

        # Optional
        caption = p.get('caption','').strip()
        start   = p.get('start_date','').strip()
        end     = p.get('end_date','').strip()
        techs   = p.get('technologiesUsed', [])
        ext     = p.get('externalSources', [])

        span = f"{start} – {end}" if start and end else start or ''

        # Header table
        tbl = Table([
            [Paragraph(name, styles['ExpTitle']), Paragraph(span, styles['ExpDate'])],
            [Paragraph(caption, styles['ExpRole']), Paragraph(loc, styles['ExpLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(tbl)

        # Details bullets
        items = [
            ListItem(Paragraph(d, styles['BodyText']), leftIndent=18, bulletIndent=0,
                     bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1)
            for d in details
        ]
        story.append(
            ListFlowable(items, bulletType='bullet', leftIndent=10, valueIndent=10,
                         spaceBefore=4, spaceAfter=0)
        )

        # External links if present
        if ext:
            links = [
                f'<a href="{src["link"]}"><font color="blue">{src["name"]}</font></a>'
                for src in ext if src.get('name') and src.get('link')
            ]
            if links:
                link_text = '<font name="CMB10">Link(s):</font> ' + ', '.join(links)
                story.append(
                    ListFlowable(
                        [ListItem(Paragraph(link_text, styles['BodyText']),
                                  leftIndent=18, bulletIndent=0,
                                  bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1)],
                        bulletType='bullet', leftIndent=10
                    )
                )

        # Technologies used if present
        if techs:
            tech_text = ', '.join(techs)
            story.append(Paragraph(f'<font name="CMB10">Technologies:</font> {tech_text}', styles['BodyText']))
            story.append(Spacer(1,5))

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 5))

# def render_projects_details(data, story, styles, doc):
#     story.append(Paragraph('Projects', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     left_col, right_col = calculateTableColumnSplit(doc)
#
#     for p in data:
#         # Header 2×2
#         span = f"{p['start_date']} – {p['end_date']}"
#         tbl = Table([
#             [Paragraph(p['projectName'], styles['EduInst']),
#              Paragraph(span, styles['EduDate'])],
#             [Paragraph(p.get('caption',''), styles['EduDegree']),
#              Paragraph(p.get('location',''), styles['EduLoc'])]
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING',  (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ]))
#         story.append(tbl)
#
#         # Project details bullets
#         items = [
#             ListItem(
#                 Paragraph(detail, styles['BodyText']),
#                 leftIndent=18, bulletIndent=0,
#                 bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1
#             )
#             for detail in p.get('projectDetails', [])
#         ]
#         if items:
#             story.append(
#                 ListFlowable(
#                     items,
#                     bulletType='bullet',
#                     leftIndent=10,
#                     valueIndent=10,
#                     spaceBefore=4,
#                     spaceAfter=0
#                 )
#             )
#
#         # Optional externalResources
#         ext = p.get('externalSources') or []
#         if ext:
#             links = [
#                 f'<a href="{src["link"]}"><font color="blue">{src["name"]}</font></a>'
#                 for src in ext
#             ]
#             link_text = f'<font name="CMB10">Link(s):</font> ' + ', '.join(links)
#             link_item = ListItem(
#                 Paragraph(link_text, styles['BodyText']),
#                 leftIndent=18, bulletIndent=0,
#                 bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1
#             )
#             story.append(
#                 ListFlowable(
#                     [link_item],
#                     bulletType='bullet',
#                     leftIndent=10,
#                     bulletFontName='CMR10',
#                     bulletFontSize=8,
#                     bulletOffsetY=-1
#                 )
#             )
#
#         # Spacer before next project
#         story.append(Spacer(1, 5))
#
#     # final bottom spacer
#     story.append(Spacer(1, 5))
def render_awards_details(data, story, styles, doc):
    """
    Renders each award if it has:
      name, type, location, date, description
    """
    if not data:
        return

    story.append(Paragraph('Awards', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for item in data:
        name = item.get('name','').strip()
        type_ = item.get('type','').strip()
        loc = item.get('location','').strip()
        date = item.get('date','').strip()
        desc = item.get('description','').strip()
        if not (name and type_ and loc and date and desc):
            continue

        location_text = f"{type_}, {loc}"
        tbl = Table([
            [Paragraph(name, styles['ExtraTitle']), Paragraph(date, styles['ExtraDate'])],
            [Paragraph(desc, styles['ExtraDesc']), Paragraph(location_text, styles['ExtraLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 5))

# def render_awards_details(data,story,styles,doc):
#     # —— Extracurricular / Achievements section ——
#     if not data:
#         return
#
#     story.append(Paragraph('Awards', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#
#     left_col, right_col = calculateTableColumnSplit(doc)
#
#     for item in data:
#         # skip if no name/date
#         name = item.get('name', '').strip()
#         date = item.get('date', '').strip()
#         if not name or not date:
#             continue
#
#         desc = item.get('description', '').strip()
#
#         loc = item.get('location', '').strip()
#         # combine institution + location
#
#
#         tbl = Table([
#             [Paragraph(name, styles['ExtraTitle']),
#              Paragraph(date, styles['ExtraDate'])],
#             [Paragraph(desc, styles['ExtraDesc']),
#              Paragraph(loc, styles['ExtraLoc'])]
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING', (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ]))
#
#         story.append(tbl)
#         story.append(Spacer(1, 2))
#
#     # a little extra space at the end
#     story.append(Spacer(1, 5))
def render_languages(data, story, styles):
    """
    Renders each language if it has:
      language, proficiency
    """
    if not data:
        return

    story.append(Paragraph('Languages', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

    for l in data:
        lang = l.get('language','').strip()
        prof = l.get('proficiency','').strip()
        if not (lang and prof):
            continue
        story.append(Paragraph(f'<font name="CMB10">{lang}:</font> {prof}', styles['BodyText']))


    story.append(Spacer(1, 5))

# def render_languages(data, story, styles):
#     story.append(Paragraph('Languages', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     for l in data:
#
#         story.append(
#             Paragraph(f'<font name="CMB10">{l["language"]}: </font>{l['proficiency']}', styles['BodyText'])
#         )
#
#     story.append(Spacer(1, 5))

def render_summary_details(data, story, styles):
    """
    Renders summary only if non-empty (optional).
    """
    text = (data or '').strip()
    if not text:
        return

    story.append(Paragraph('Summary', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    story.append(Paragraph(text, styles['BodyText']))
    story.append(Spacer(1, 10))

# def render_summary_details(data, story, styles):
#     story.append(Paragraph('Summary', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#     story.append(Paragraph(data, styles['BodyText']))
#     story.append(Spacer(1, 12))


def render_certifications(data, story, styles, doc):
    """
    Renders each certification if it has:
      name, issuing_organization, issue_date, expiration_date, credential_id, url
    """
    if not data:
        return

    story.append(Paragraph('Certifications', styles['SectionHeading']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    left_col, right_col = calculateTableColumnSplit(doc)

    for item in data:
        name  = item.get('name','').strip()
        org   = item.get('issuing_organization','').strip()
        issue = item.get('issue_date','').strip()
        exp   = item.get('expiration_date','').strip()
        cred  = item.get('credential_id','').strip()
        url   = item.get('url','').strip()
        if not (name and org and issue and exp and cred and url):
            continue

        date_span = f"{issue} – {exp}"
        cred_cell = Paragraph(f'<a href="{url}"><u>{cred}</u></a>', styles['ExtraDesc'])

        tbl = Table([
            [Paragraph(name, styles['ExtraTitle']), Paragraph(date_span, styles['ExtraDate'])],
            [cred_cell, Paragraph(org, styles['ExtraLoc'])]
        ], colWidths=[left_col, right_col])
        tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 5))
#
# def render_certifications(data, story, styles, doc):
#     if not data:
#         return
#
#     story.append(Paragraph('Certifications', styles['SectionHeading']))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
#
#     left_col, right_col = calculateTableColumnSplit(doc)
#
#     for item in data:
#         name        = item.get('name', '').strip()
#         issued_org  = item.get('issuing_organization', '').strip()
#         cred_id     = item.get('credential_id', '').strip()
#         url         = item.get('url', '').strip()
#         date_span   = f"{item.get('issue_date','')} – {item.get('expiration_date','')}"
#
#         if not name or not date_span:
#             continue
#
#         # build credential ID cell: link+underline if URL present, else plain text
#         if cred_id and url:
#             cred_cell = Paragraph(f'<a href="{url}"><u>{cred_id}</u></a>', styles['ExtraDesc'])
#         else:
#             cred_cell = Paragraph(cred_id, styles['ExtraDesc'])
#
#         tbl = Table([
#             [Paragraph(name,       styles['ExtraTitle']),
#              Paragraph(date_span,  styles['ExtraDate'])],
#             [cred_cell,
#              Paragraph(issued_org, styles['ExtraLoc'])]
#         ], colWidths=[left_col, right_col])
#         tbl.setStyle(TableStyle([
#             ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING',  (0, 0), (-1, -1), 0),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
#         ]))
#
#         story.append(tbl)
#         story.append(Spacer(1, 2))
#
#     story.append(Spacer(1, 5))

def _set_metadata(canvas, document):
    canvas.setAuthor('vaishnav')
    canvas.setTitle('vaishnav')
    # if you want you can also set subject/keywords:
    # canvas.setSubject('Resume of Vaishnav')
    # canvas.setKeywords('resume, vaishnav, pdf')

def build_pdf(buffer,data):
    author_name = data['personal_information']['name']
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.3*inch, rightMargin=0.3*inch,
        topMargin=0.3*inch, bottomMargin=0.3*inch
    )


    styles = resumeStyling()
    story = []
    render_personal_info(data['personal_information'],story,styles)

    render_education_details(data['education'],story,styles,doc)

    render_experiences_details(data['experiences'],story,styles,doc)

    render_skills_details(data['skills'],story,styles)

    render_projects_details(data['projects'],story,styles,doc)

    render_extras_details(data['extracurricular/achievements'],story,styles,doc)

    render_languages(data['languages'],story,styles)

    render_summary_details(data['summary'], story, styles)

    render_awards_details(data['awards'],story,styles,doc)

    render_certifications(data['certifications'],story,styles,doc)


    def _set_metadata(canvas, document):
        canvas.setAuthor(author_name)
        canvas.setTitle(f"{author_name} Resume")

    doc.build(
        story,
        onFirstPage=_set_metadata,
        onLaterPages=_set_metadata
    )

@app.route('/resume')
def resume():
    # load your JSON from file or other source
    with open('schema.json') as f:
        resume_data = json.load(f)

    buf = io.BytesIO()
    build_pdf(buf, resume_data)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=False,
        download_name='Resume.pdf'
    )



if __name__ == '__main__':
    app.run(debug=True)
