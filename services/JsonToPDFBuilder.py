import io
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, ListFlowable, ListItem, HRFlowable, Spacer)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle
from typing import Optional, List


class JsonToPDFBuilder:
    def __init__(self):
        # Register fonts
        pdfmetrics.registerFont(TTFont('CMR10', '../data/fonts/cmunrm.ttf'))  # Roman
        pdfmetrics.registerFont(TTFont('CMB10', '../data/fonts/cmunbx.ttf'))  # Bold
        pdfmetrics.registerFont(TTFont('CMIT10', '../data/fonts/cmunti.ttf'))  # Italic
        pdfmetrics.registerFont(TTFont('BodoniMT', '../data/fonts/bodoni-mt-regular.ttf'))
        self.story = []
        self.styles = self.resumeStyling()
        # Default rendering order
        self.default_order = [
            'personal_info',
            'education',
            'experiences',
            'skills',
            'projects',
            'extras',
            'languages',
            'summary',
            'awards',
            'certifications',
        ]

    @staticmethod
    def safe_strip(value):
        """Return stripped string if not None, else empty string."""
        return value.strip() if isinstance(value, str) else ''

    def calculateTableColumnSplit(self, doc):
        # Compute 2:1 column widths
        page_w, _ = letter
        usable_w = page_w - doc.leftMargin - doc.rightMargin
        left_col = usable_w * 1.94 / 3
        right_col = usable_w * 1 / 3
        return left_col, right_col

    def resumeStyling(self):
        large = 12
        small = 11
        xSmall = 10
        huge = 22.74
        self.styles = getSampleStyleSheet()
        # —— Body text ——
        self.styles['BodyText'].fontName = 'CMR10'
        self.styles['BodyText'].fontSize = xSmall
        self.styles['BodyText'].leading = small
        self.styles['BodyText'].spaceAfter = 0
        self.styles['BodyText'].alignment = TA_JUSTIFY

        # —— Name ——
        self.styles.add(ParagraphStyle(
            name='Name',
            fontName='BodoniMT',
            fontSize=huge,
            leading=10,
            alignment=1,
            spaceAfter=18,
        ))
        # —— Name ——
        self.styles.add(ParagraphStyle(
            name='headerLoc',
            fontName='CMR10',
            fontSize=small,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=8,

        ))

        # —— Contact line ——
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            fontName='CMR10',
            fontSize=xSmall,
            leading=12,
            alignment=1,
            spaceAfter=12
        ))

        # —— Section heading (bold, uppercase) ——
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            fontName='CMB10',
            fontSize=large,
            leading=large,

            spaceAfter=5,
            alignment=0,
            uppercase=True
        ))

        # —— Education table styles ——
        self.styles.add(ParagraphStyle(
            name='EduInst',
            fontName='CMB10',
            fontSize=xSmall,
            leading=8,
        ))
        self.styles.add(ParagraphStyle(
            name='EduDegree',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=8,
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='EduDate',
            fontName='CMB10',
            fontSize=xSmall,
            leading=8,
            alignment=2  # right
        ))
        self.styles.add(ParagraphStyle(
            name='EduLoc',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=8,
            alignment=2,  # right
            spaceAfter=1
        ))

        # —— Experience table styles ——
        self.styles.add(ParagraphStyle(
            name='ExpTitle',
            fontName='CMB10',
            fontSize=small,
            leading=8,
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExpRole',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=xSmall,

        ))
        self.styles.add(ParagraphStyle(
            name='ExpDate',
            fontName='CMB10',
            fontSize=small,
            leading=8,
            alignment=2,  # right
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExpLoc',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=8,
            alignment=2,  # right
            spaceAfter=0
        ))

        # —— Extracurricular / Achievements styles ——
        self.styles.add(ParagraphStyle(
            name='ExtraTitle',
            fontName='CMB10',
            fontSize=small,
            leading=xSmall,
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExtraDesc',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=xSmall,
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExtraDate',
            fontName='CMB10',
            fontSize=small,
            leading=xSmall,
            alignment=2,  # right
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExtraLoc',
            fontName='CMIT10',
            fontSize=xSmall,
            leading=xSmall,
            alignment=2,  # right
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='skill',
            fontName='CMR10',
            fontSize=xSmall,
            leading=small,
            spaceBefore=2,

            spaceAfter=0,
        ))
        return self.styles

    def render_personal_info(self, data):
        """
        Renders:
         - name (required)
         - location (required)
         - phone, email (required)
         - socials (optional)
        """
        name = self.safe_strip(data.get('name', ''))
        location = self.safe_strip(data.get('location', ''))
        phone = self.safe_strip(data.get('phone', ''))
        email = self.safe_strip(data.get('email', ''))
        if not (name and location and phone and email):
            return

        self.story.append(Paragraph(name, self.styles['Name']))
        self.story.append(Paragraph(location, self.styles['headerLoc']))
        SEP = '&nbsp;&nbsp;&nbsp;&nbsp;'
        parts = []

        # Phone
        parts.append(f'<img src="data/images/phone.png" width="10" height="10"/>&nbsp;{phone}')

        # Email
        parts.append(
            f'<img src="data/images/mail.png" width="10" height="10"/>&nbsp;'
            f'<a href="mailto:{email}"><u>{email}</u></a>'
        )

        # Optional socials
        for soc in data.get('socials', []):
            name = self.safe_strip(soc.get('name', ''))
            link = self.safe_strip(soc.get('link', ''))
            if not (name and link):
                continue
            icon = f'data/images/{name.lower()}.png'
            parts.append(
                f'<img src="{icon}" width="10" height="10"/>&nbsp;'
                f'<a href="{link}"><u>{name}</u></a>'
            )

        self.story.append(Paragraph(SEP.join(parts), self.styles['HeaderInfo']))

    def render_education_details(self, edus, doc):
        """
        Renders each education entry if it has all required fields:
          institution, degree, location, start_date, gpa, gpa_out_off
        end_date is optional.
        """
        if not edus:
            return

        self.story.append(Paragraph('Education', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        left_col, right_col = self.calculateTableColumnSplit(doc)

        for ed in edus:
            inst = self.safe_strip(ed.get('institution', ''))
            deg = self.safe_strip(ed.get('degree', ''))
            loc = self.safe_strip(ed.get('location', ''))
            start = self.safe_strip(ed.get('start_date', ''))
            gpa = self.safe_strip(ed.get('gpa', ''))
            out_off = self.safe_strip(ed.get('gpa_out_off', ''))
            if not (inst and deg and loc and start and gpa and out_off):
                continue

            # Optional end date
            end = self.safe_strip(ed.get('end_date', ''))
            span = f"{start} – {end}" if end else start
            degree_text = f"{deg}, GPA {gpa}/{out_off}"

            tbl = Table([
                [Paragraph(inst, self.styles['EduInst']), Paragraph(span, self.styles['EduDate'])],
                [Paragraph(degree_text, self.styles['EduDegree']), Paragraph(loc, self.styles['EduLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))

            self.story.append(tbl)
            self.story.append(Spacer(1, 5))

        self.story.append(Spacer(1, 5))

    def render_experiences_details(self, exps, doc):
        """
        Renders each experience entry if it has:
          designation, companyName, location, start_date
        Optional: end_date, caption, points
        """
        if not exps:
            return

        self.story.append(Paragraph('Experience', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        left_col, right_col = self.calculateTableColumnSplit(doc)

        # Tight bullet paragraph style
        bullet_style = ParagraphStyle(
            'BulletTight',
            parent=self.styles['BodyText'],
            spaceBefore=4,
            spaceAfter=0,
            leading=self.styles['BodyText'].fontSize * 1.1
        )

        for e in exps:
            desig = self.safe_strip(e.get('designation', ''))
            comp = self.safe_strip(e.get('companyName', ''))
            loc = self.safe_strip(e.get('location', ''))
            start = self.safe_strip(e.get('start_date', ''))
            if not (desig and comp and loc and start):
                continue

            end = self.safe_strip(e.get('end_date', ''))
            caption = self.safe_strip(e.get('caption', ''))
            points = e.get('points', [])
            span = f"{start} – {end}" if end else start

            # Header: designation & date, company & location
            tbl = Table([
                [Paragraph(desig, self.styles['ExpTitle']), Paragraph(span, self.styles['ExpDate'])],
                [Paragraph(comp if not caption else caption, self.styles['ExpRole']),
                 Paragraph(loc, self.styles['ExpLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            self.story.append(tbl)
            # small gap before bullets
            self.story.append(Spacer(1, 2))

            # Bullet points if present, with tight spacing
            if points:
                items = [
                    ListItem(
                        Paragraph(pt, bullet_style),
                        leftIndent=18,
                        bulletIndent=0,
                        bulletFontName='CMR10',
                        bulletFontSize=8,
                        bulletOffsetY=-1
                    )
                    for pt in points
                ]
                self.story.append(
                    ListFlowable(
                        items,
                        bulletType='bullet',
                        leftIndent=10,
                        spaceBefore=0,
                        spaceAfter=0
                    )
                )

            # minimal gap after each experience
            self.story.append(Spacer(1, 3))

        # final bottom spacer
        self.story.append(Spacer(1, 5))

    # def render_experiences_details(self,exps,doc):
    #     """
    #     Renders each experience entry if it has:
    #       designation, companyName, location, start_date
    #     Optional: end_date, caption, points
    #     """
    #     if not exps:
    #         return
    #
    #     self.story.append(Paragraph('Experience', self.styles['SectionHeading']))
    #     self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    #     left_col, right_col = self.calculateTableColumnSplit(doc)
    #
    #     for e in exps:
    #         desig = self.safe_strip(e.get('designation',''))
    #         comp  = self.safe_strip(e.get('companyName',''))
    #         loc   = self.safe_strip(e.get('location',''))
    #         start = self.safe_strip(e.get('start_date',''))
    #         if not (desig and comp and loc and start):
    #             continue
    #
    #         # Optional fields
    #         end     = self.safe_strip(e.get('end_date',''))
    #         caption = self.safe_strip(e.get('caption',''))
    #         points  = e.get('points', [])
    #
    #         span = f"{start} – {end}" if end else start
    #
    #         # Header: designation & date, company & location
    #         tbl = Table([
    #             [Paragraph(desig, self.styles['ExpTitle']), Paragraph(span, self.styles['ExpDate'])],
    #             [Paragraph(comp if not caption else caption, self.styles['ExpRole']),
    #              Paragraph(loc, self.styles['ExpLoc'])]
    #         ], colWidths=[left_col, right_col])
    #         tbl.setStyle(TableStyle([
    #             ('VALIGN',(0,0),(-1,-1),'TOP'),
    #             ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
    #         ]))
    #         self.story.append(tbl)
    #
    #         # Bullet points if present
    #         if points:
    #             items = [
    #                 ListItem(Paragraph(pt, self.styles['BodyText']), leftIndent=18, bulletIndent=0)
    #                 for pt in points
    #             ]
    #             self.story.append(
    #                 ListFlowable(items,
    #                     bulletType='bullet', bulletFontName='CMR10',
    #                     bulletFontSize=8, bulletOffsetY=-1, leftIndent=10
    #                 )
    #             )
    #         self.story.append(Spacer(1, 5))
    #
    #     self.story.append(Spacer(1, 5))

    def render_skills_details(self, data):
        """
        Renders each skill category if it has:
          name, data (non-empty list)
        """
        if not data:
            return

        self.story.append(Paragraph('Technical Skills', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

        for sk in data:
            name = self.safe_strip(sk.get('name', ''))
            items = sk.get('data', [])
            if not (name and items):
                continue

            skills_text = ', '.join(items)
            self.story.append(
                Paragraph(f'<font name="CMB10">{name}:</font> {skills_text}', self.styles['BodyText'])
            )
            # self.story.append(Spacer(1, 2))

        self.story.append(Spacer(1, 8))

    def render_extras_details(self, data, doc):
        """
        Renders each extracurricular/achievement if it has:
          name, type, location, date, description
        """
        if not data:
            return

        self.story.append(Paragraph('Extracurricular / Achievements', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        left_col, right_col = self.calculateTableColumnSplit(doc)

        for item in data:
            name = self.safe_strip(item.get('name', ''))
            type_ = self.safe_strip(item.get('type', ''))
            loc = self.safe_strip(item.get('location', ''))
            date = self.safe_strip(item.get('date', ''))
            desc = self.safe_strip(item.get('description', ''))
            if not (name and type_ and loc and date and desc):
                continue

            tbl = Table([
                [Paragraph(name, self.styles['ExtraTitle']), Paragraph(date, self.styles['ExtraDate'])],
                [Paragraph(desc, self.styles['ExtraDesc']), Paragraph(loc, self.styles['ExtraLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            self.story.append(tbl)
            self.story.append(Spacer(1, 2))

        self.story.append(Spacer(1, 5))

    def render_projects_details(self, data, doc):
        """
        Renders each project if it has:
          projectName, location, projectDetails (non-empty list)
        Optional: caption, start_date, end_date, url, externalSources, technologiesUsed
        """
        if not data:
            return

        self.story.append(Paragraph('Projects', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

        left_col, right_col = self.calculateTableColumnSplit(doc)

        # define a tighter bullet paragraph style
        bullet_style = ParagraphStyle(
            'BulletTight',
            parent=self.styles['BodyText'],
            spaceBefore=4,
            spaceAfter=0,
            leading=self.styles['BodyText'].fontSize * 1.1
        )

        for p in data:
            name = self.safe_strip(p.get('projectName', ''))
            loc = self.safe_strip(p.get('location', ''))
            details = p.get('projectDetails', [])
            if not (name and loc and details):
                continue

            caption = self.safe_strip(p.get('caption', ''))
            start = self.safe_strip(p.get('start_date', ''))
            end = self.safe_strip(p.get('end_date', ''))
            techs = p.get('technologiesUsed', [])
            ext = p.get('externalSources', [])
            span = f"{start} – {end}" if start and end else start or ''

            # Header table
            tbl = Table([
                [Paragraph(name, self.styles['ExpTitle']), Paragraph(span, self.styles['ExpDate'])],
                [Paragraph(caption, self.styles['ExpRole']), Paragraph(loc, self.styles['ExpLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            self.story.append(tbl)
            self.story.append(Spacer(1, 2))
            # Details bullets (no extra padding on list or items)
            items = [
                ListItem(
                    Paragraph(d, bullet_style),
                    leftIndent=18,
                    bulletIndent=0,
                    bulletFontName='CMR10',
                    bulletFontSize=8,
                    bulletOffsetY=-1

                )
                for d in details
            ]
            self.story.append(
                ListFlowable(
                    items,
                    bulletType='bullet',
                    leftIndent=10,
                    valueIndent=10,
                    spaceBefore=4,
                    spaceAfter=0

                )
            )

            # External links if present
            if ext:
                links = [
                    f'<a href="{src["link"]}"><font color="blue">{src["name"]}</font></a>'
                    for src in ext if src.get('name') and src.get('link')
                ]
                if links:
                    link_text = '<font name="CMB10">Link(s):</font> ' + ', '.join(links)
                    self.story.append(
                        ListFlowable(
                            [ListItem(
                                Paragraph(link_text, bullet_style),
                                leftIndent=18,
                                bulletIndent=0,
                                bulletFontName='CMR10',
                                bulletFontSize=8,
                                bulletOffsetY=-1
                            )],
                            bulletType='bullet',
                            leftIndent=10,
                            spaceBefore=4,
                            spaceAfter=0
                        )
                    )

            # Technologies used if present
            if techs:
                tech_text = ', '.join(techs)
                self.story.append(
                    Paragraph(f'<font name="CMB10">Technologies:</font> {tech_text}', self.styles['BodyText'])
                )

            # smaller spacer between projects
            self.story.append(Spacer(1, 3))

        # final bottom spacer
        self.story.append(Spacer(1, 5))

    # def render_projects_details(self,data, doc):
    #     """
    #     Renders each project if it has:
    #       projectName, location, projectDetails (non-empty list)
    #     Optional: caption, start_date, end_date, url, externalSources, technologiesUsed
    #     """
    #     if not data:
    #         return
    #
    #     self.story.append(Paragraph('Projects', self.styles['SectionHeading']))
    #     self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    #     left_col, right_col = self.calculateTableColumnSplit(doc)
    #
    #     for p in data:
    #         name     = self.safe_strip(p.get('projectName',''))
    #         loc      = self.safe_strip(p.get('location',''))
    #         details  = p.get('projectDetails', [])
    #         if not (name and loc and details):
    #             continue
    #
    #         # Optional
    #         caption = self.safe_strip(p.get('caption',''))
    #         start   = self.safe_strip(p.get('start_date',''))
    #         end     = self.safe_strip(p.get('end_date',''))
    #         techs   = p.get('technologiesUsed', [])
    #         ext     = p.get('externalSources', [])
    #
    #         span = f"{start} – {end}" if start and end else start or ''
    #
    #         # Header table
    #         tbl = Table([
    #             [Paragraph(name, self.styles['ExpTitle']), Paragraph(span, self.styles['ExpDate'])],
    #             [Paragraph(caption, self.styles['ExpRole']), Paragraph(loc, self.styles['ExpLoc'])]
    #         ], colWidths=[left_col, right_col])
    #         tbl.setStyle(TableStyle([
    #             ('VALIGN',(0,0),(-1,-1),'TOP'),
    #             ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
    #         ]))
    #         self.story.append(tbl)
    #
    #         # Details bullets
    #         items = [
    #             ListItem(Paragraph(d, self.styles['BodyText']), leftIndent=18, bulletIndent=0,
    #                      bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1)
    #             for d in details
    #         ]
    #         self.story.append(
    #             ListFlowable(items, bulletType='bullet', leftIndent=10, valueIndent=10,
    #                          spaceBefore=4, spaceAfter=0)
    #         )
    #
    #         # External links if present
    #         if ext:
    #             links = [
    #                 f'<a href="{src["link"]}"><font color="blue">{src["name"]}</font></a>'
    #                 for src in ext if src.get('name') and src.get('link')
    #             ]
    #             if links:
    #                 link_text = '<font name="CMB10">Link(s):</font> ' + ', '.join(links)
    #                 self.story.append(
    #                     ListFlowable(
    #                         [ListItem(Paragraph(link_text, self.styles['BodyText']),
    #                                   leftIndent=18, bulletIndent=0,
    #                                   bulletFontName='CMR10', bulletFontSize=8, bulletOffsetY=-1)],
    #                         bulletType='bullet', leftIndent=10
    #                     )
    #                 )
    #
    #         # Technologies used if present
    #         if techs:
    #             tech_text = ', '.join(techs)
    #             self.story.append(Paragraph(f'<font name="CMB10">Technologies:</font> {tech_text}', self.styles['BodyText']))
    #             self.story.append(Spacer(1,5))
    #
    #         self.story.append(Spacer(1, 5))
    #
    #     self.story.append(Spacer(1, 5))

    def render_awards_details(self, data, doc):
        """
        Renders each award if it has:
          name, type, location, date, description
        """
        if not data:
            return

        self.story.append(Paragraph('Awards', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        left_col, right_col = self.calculateTableColumnSplit(doc)

        for item in data:
            name = self.safe_strip(item.get('name', ''))
            type_ = self.safe_strip(item.get('type', ''))
            loc = self.safe_strip(item.get('location', ''))
            date = self.safe_strip(item.get('date', ''))
            desc = self.safe_strip(item.get('description', ''))
            if not (name and type_ and loc and date and desc):
                continue

            location_text = f"{type_}, {loc}"
            tbl = Table([
                [Paragraph(name, self.styles['ExtraTitle']), Paragraph(date, self.styles['ExtraDate'])],
                [Paragraph(desc, self.styles['ExtraDesc']), Paragraph(location_text, self.styles['ExtraLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            self.story.append(tbl)
            self.story.append(Spacer(1, 2))

        self.story.append(Spacer(1, 5))

    def render_languages(self, data):
        """
        Renders each language if it has:
          language, proficiency
        """
        if not data:
            return

        self.story.append(Paragraph('Languages', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))

        for l in data:
            lang = self.safe_strip(l.get('language', ''))
            prof = self.safe_strip(l.get('proficiency', ''))
            if not (lang and prof):
                continue
            self.story.append(Paragraph(f'<font name="CMB10">{lang}:</font> {prof}', self.styles['BodyText']))

        self.story.append(Spacer(1, 5))

    def render_summary_details(self, data):
        """
        Renders summary only if non-empty (optional).
        """
        text = self.safe_strip((data or ''))
        if not text:
            return

        self.story.append(Paragraph('Summary', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        self.story.append(Paragraph(text, self.styles['BodyText']))
        self.story.append(Spacer(1, 10))

    def render_certifications(self, data, doc):
        """
        Renders each certification if it has:
          name, issuing_organization, issue_date, expiration_date, credential_id, url
        """
        if not data:
            return

        self.story.append(Paragraph('Certifications', self.styles['SectionHeading']))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
        left_col, right_col = self.calculateTableColumnSplit(doc)

        for item in data:
            name = self.safe_strip(item.get('name', ''))
            org = self.safe_strip(item.get('issuing_organization', ''))
            issue = self.safe_strip(item.get('issue_date', ''))
            exp = self.safe_strip(item.get('expiration_date', ''))
            cred = self.safe_strip(item.get('credential_id', ''))
            url = self.safe_strip(item.get('url', ''))
            if not (name and org and issue and exp and cred and url):
                continue

            date_span = f"{issue} – {exp}"
            cred_cell = Paragraph(f'<a href="{url}"><u>{cred}</u></a>', self.styles['ExtraDesc'])

            tbl = Table([
                [Paragraph(name, self.styles['ExtraTitle']), Paragraph(date_span, self.styles['ExtraDate'])],
                [cred_cell, Paragraph(org, self.styles['ExtraLoc'])]
            ], colWidths=[left_col, right_col])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            self.story.append(tbl)
            self.story.append(Spacer(1, 2))

        self.story.append(Spacer(1, 5))

    def build_pdf(self, buffer, data, order: Optional[List[str]] = None):
        author_name = data['personal_information']['name']
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.3 * inch, rightMargin=0.3 * inch,
            topMargin=0.3 * inch, bottomMargin=0.3 * inch
        )

        styles = self.resumeStyling()
        # pick the sequence
        seq = order or self.default_order

        # map keys to the actual render calls
        section_map = {
            'personal_info': lambda: self.render_personal_info(data.get('personal_information', {})),
            'education': lambda: self.render_education_details(data.get('education', []), doc),
            'experiences': lambda: self.render_experiences_details(data.get('experiences', []), doc),
            'skills': lambda: self.render_skills_details(data.get('skills', [])),
            'projects': lambda: self.render_projects_details(data.get('projects', []), doc),
            'extras': lambda: self.render_extras_details(data.get('extracurricular/achievements', []), doc),
            'languages': lambda: self.render_languages(data.get('languages', [])),
            'summary': lambda: self.render_summary_details(data.get('summary', '')),
            'awards': lambda: self.render_awards_details(data.get('awards', []), doc),
            'certifications': lambda: self.render_certifications(data.get('certifications', []), doc),
        }

        # execute in order
        for key in seq:
            renderer = section_map.get(key)
            if not renderer:
                raise ValueError(f"Unknown section key: {key!r}")
            renderer()

        def _set_metadata(canvas, document):
            canvas.setAuthor(author_name)
            canvas.setTitle(f"{author_name} Resume")

        doc.build(
            self.story,
            onFirstPage=_set_metadata,
            onLaterPages=_set_metadata
        )

    def build(self, json_data, order: Optional[List[str]] = None):
        buf = io.BytesIO()
        self.build_pdf(buf, json_data, order)
        buf.seek(0)
        return buf.getvalue()  # Return the PDF content as bytes
