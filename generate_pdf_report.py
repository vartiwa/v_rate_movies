"""
Generate a comprehensive, publication-grade PDF report and presentation guide
for the v_rate_movies project.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page numbers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "v_rate_movies • Project Architecture & Presentation Guide")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Author: vartiwa (varunt154@gmail.com)")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 46, 8.5 * inch - 54, 46)
        
        self.drawString(54, 32, "https://github.com/vartiwa/v_rate_movies • FiveThirtyEight Replication Study")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_text)
        self.restoreState()


def build_pdf():
    pdf_filename = "v_rate_movies_project_guide.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#6366f1")
    c_dark = colors.HexColor("#0f172a")
    c_crimson = colors.HexColor("#f43f5e")
    c_emerald = colors.HexColor("#10b981")
    c_sub = colors.HexColor("#334155")
    c_dim = colors.HexColor("#64748b")
    c_bg_subtle = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#e2e8f0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_dark,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_sub,
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_primary,
        spaceAfter=16
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_dark,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_sub,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_sub,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_sub
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_dark
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title Block
    story.append(Paragraph("v_rate_movies", title_style))
    story.append(Paragraph("Movie Ratings Bias Investigation, Cross-Platform Intelligence & Presentation Guide", subtitle_style))
    story.append(Paragraph("Author: vartiwa (varunt154@gmail.com) • Repository: github.com/vartiwa/v_rate_movies", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=14))

    # Section 1: Executive Overview
    story.append(Paragraph("1. Executive Summary & Context", h1_style))
    story.append(Paragraph(
        "<b>What is this project?</b> <i>v_rate_movies</i> is a production-grade data-journalism replication, statistical audit, "
        "and interactive intelligence suite investigating movie rating bias on Fandango. It reproduces and extends Walt Hickey's "
        "landmark 2015 <i>FiveThirtyEight</i> investigation: <i>'Be Suspicious Of Online Movie Ratings, Especially Fandango's'</i>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Core Mystery:</b> In 2015, Hickey noticed that movie star ratings displayed on Fandango were almost universally "
        "higher than ratings on Rotten Tomatoes, Metacritic, and IMDB. A closer inspection of Fandango's raw HTML revealed that "
        "the visual star icons presented to users did not match the underlying calculated ratings.",
        body_style
    ))

    # Summary KPI Box
    kpi_data = [
        [
            Paragraph("<b>+0.24 ★</b><br/><font size=7 color='#64748b'>Avg Inflation Delta</font>", callout_style),
            Paragraph("<b>89.0%</b><br/><font size=7 color='#64748b'>Films Rounded Up</font>", callout_style),
            Paragraph("<b>4.09 ★ vs 3.85 ★</b><br/><font size=7 color='#64748b'>Displayed vs True HTML</font>", callout_style),
            Paragraph("<b>3.89 ★</b><br/><font size=7 color='#64748b'>2016–17 Post Drop</font>", callout_style),
            Paragraph("<b>p &lt; 10⁻¹⁵</b><br/><font size=7 color='#64748b'>Paired t-test (d = 1.34)</font>", callout_style),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[100, 95, 120, 95, 94])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_subtle),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # Section 2: How the Rounding Glitch Worked
    story.append(Paragraph("2. The Mechanism: How the Rounding Glitch Worked", h1_style))
    story.append(Paragraph(
        "Fandango displayed star ratings in increments of half-stars (3.5, 4.0, 4.5, 5.0). Standard mathematical half-rounding "
        "rounds a value to the nearest 0.5 increment (e.g., 4.1 rounds to 4.0; 4.3 rounds to 4.5).",
        body_style
    ))
    story.append(Paragraph(
        "However, Fandango's frontend software contained an asymmetric, ceiling-biased algorithm:",
        body_style
    ))

    story.append(Paragraph("• <b>The Glitch Rule:</b> If a film's true calculated score had any fractional part as small as <b>0.1</b>, "
                           "Fandango's code bumped it up to the next half-star (e.g., <b>4.1 → 4.5★</b>; <b>4.6 → 5.0★</b>).", bullet_style))
    story.append(Paragraph("• <b>Ceiling Inflation:</b> 130 of 146 films (<b>89.04%</b>) had displayed stars strictly higher than their true HTML ratings. "
                           "Zero films were rounded down.", bullet_style))
    story.append(Paragraph("• <b>Maximum Discrepancy:</b> Several major films received an unearned boost of <b>+0.50 full stars</b> "
                           "(e.g., <i>Avengers: Age of Ultron</i>, <i>Cinderella</i>, <i>Ant-Man</i>, <i>The Water Diviner</i>).", bullet_style))

    story.append(Spacer(1, 8))

    # Rounding Comparison Table
    round_data = [
        [Paragraph("True HTML Rating", table_header), Paragraph("Standard Math Round", table_header), Paragraph("Fandango Displayed", table_header), Paragraph("Artificial Delta", table_header), Paragraph("Effect Status", table_header)],
        [Paragraph("4.1 / 5.0", table_cell_bold), Paragraph("4.0 ★", table_cell), Paragraph("4.5 ★", table_cell_bold), Paragraph("+0.4 ★", table_cell), Paragraph("<font color='#f43f5e'>Glitch Boosted</font>", table_cell)],
        [Paragraph("4.2 / 5.0", table_cell_bold), Paragraph("4.0 ★", table_cell), Paragraph("4.5 ★", table_cell_bold), Paragraph("+0.3 ★", table_cell), Paragraph("<font color='#f43f5e'>Glitch Boosted</font>", table_cell)],
        [Paragraph("4.5 / 5.0", table_cell_bold), Paragraph("4.5 ★", table_cell), Paragraph("5.0 ★", table_cell_bold), Paragraph("+0.5 ★", table_cell), Paragraph("<font color='#f43f5e'>Glitch Boosted</font>", table_cell)],
        [Paragraph("4.6 / 5.0", table_cell_bold), Paragraph("4.5 ★", table_cell), Paragraph("5.0 ★", table_cell_bold), Paragraph("+0.4 ★", table_cell), Paragraph("<font color='#f43f5e'>Glitch Boosted</font>", table_cell)],
        [Paragraph("4.0 / 5.0", table_cell_bold), Paragraph("4.0 ★", table_cell), Paragraph("4.0 ★", table_cell), Paragraph("0.0 ★", table_cell), Paragraph("<font color='#10b981'>Exact Match</font>", table_cell)],
    ]
    round_table = Table(round_data, colWidths=[90, 105, 105, 95, 109])
    round_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(round_table)

    story.append(Spacer(1, 14))

    # Section 3: Cross-Platform Disparities
    story.append(Paragraph("3. Cross-Platform Benchmark & Critic Disparities", h1_style))
    story.append(Paragraph(
        "To benchmark Fandango against the broader movie ecosystem, all ratings were normalized onto a 0 to 5-star scale "
        "(Rotten Tomatoes / 20, Metacritic / 20, IMDB / 2):",
        body_style
    ))

    # Platform Table
    plat_data = [
        [Paragraph("Review Platform", table_header), Paragraph("Mean Rating", table_header), Paragraph("Median", table_header), Paragraph("Std Dev", table_header), Paragraph("Range", table_header), Paragraph("Distribution Character", table_header)],
        [Paragraph("Fandango (Displayed)", table_cell_bold), Paragraph("4.09 ★", table_cell_bold), Paragraph("4.00 ★", table_cell), Paragraph("0.54", table_cell), Paragraph("3.0 - 5.0", table_cell), Paragraph("<font color='#f43f5e'>Severe Rightward Skew</font>", table_cell)],
        [Paragraph("Fandango (Actual HTML)", table_cell_bold), Paragraph("3.85 ★", table_cell), Paragraph("3.90 ★", table_cell), Paragraph("0.50", table_cell), Paragraph("2.7 - 4.8", table_cell), Paragraph("Moderate Right Skew", table_cell)],
        [Paragraph("IMDB (Normalized)", table_cell), Paragraph("3.37 ★", table_cell), Paragraph("3.30 ★", table_cell), Paragraph("0.48", table_cell), Paragraph("2.0 - 4.3", table_cell), Paragraph("Bell-shaped Normal", table_cell)],
        [Paragraph("Rotten Tomatoes (Norm)", table_cell), Paragraph("3.04 ★", table_cell), Paragraph("3.00 ★", table_cell), Paragraph("1.51", table_cell), Paragraph("0.2 - 4.9", table_cell), Paragraph("Wide Uniform Spread", table_cell)],
        [Paragraph("Metacritic (Norm)", table_cell), Paragraph("2.94 ★", table_cell), Paragraph("2.95 ★", table_cell), Paragraph("0.98", table_cell), Paragraph("0.6 - 4.7", table_cell), Paragraph("True Normal Gaussian", table_cell)],
    ]
    plat_table = Table(plat_data, colWidths=[120, 75, 65, 55, 75, 114])
    plat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(plat_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Egregious Critic Disparities:</b> Films that were universally panned by critics were nonetheless "
                           "awarded 4 to 5 stars on Fandango:", body_style))
    story.append(Paragraph("• <i>Do You Believe? (2015)</i>: Rotten Tomatoes gave it <b>18% (0.9★)</b>; Fandango displayed <b>5.0 Stars</b> (+4.10★ gap!).", bullet_style))
    story.append(Paragraph("• <i>Taken 3 (2015)</i>: Rotten Tomatoes gave it <b>9% (0.45★)</b>; Fandango displayed <b>4.5 Stars</b> (+4.05★ gap!).", bullet_style))
    story.append(Paragraph("• <i>Pixels (2015)</i>: Rotten Tomatoes gave it <b>17% (0.85★)</b>; Fandango displayed <b>4.5 Stars</b> (+3.65★ gap!).", bullet_style))

    story.append(PageBreak())

    # Section 4: The Commercial Incentive
    story.append(Paragraph("4. The Business Conflict of Interest", h1_style))
    story.append(Paragraph(
        "<b>Why did this happen?</b> Understanding the commercial incentives explains why the glitch remained unaddressed for so long:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Aggregators vs. Brokers:</b> Rotten Tomatoes and Metacritic are media aggregators whose revenue is driven by pageviews "
        "and advertising. Fandango is an <b>online movie ticket broker</b> that collects convenience fees per ticket sold.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Conversion Optimization:</b> In e-commerce checkout funnels, higher ratings directly decrease user hesitation and increase "
        "ticket conversion rates. By ensuring no film ever displayed below 3.0 stars and 89% displayed 4.0+ stars, Fandango created an "
        "artificial halo effect that optimized ticket purchasing behavior.",
        bullet_style
    ))

    story.append(Spacer(1, 10))

    # Section 5: Temporal Shift (2015 vs 2016-17)
    story.append(Paragraph("5. Temporal Audit: Did Fandango Fix It? (2015 vs 2016–17)", h1_style))
    story.append(Paragraph(
        "In response to Hickey's report, Fandango claimed the issue was an accidental software bug and promised a remediation. "
        "An audit of 214 films released after the article (2016–2017) proves that Fandango indeed adjusted their display code:",
        body_style
    ))

    story.append(Paragraph("• <b>Net Drop in Displayed Stars:</b> 2015 Displayed Mean = <b>4.089★</b> vs. 2016–17 Displayed Mean = <b>3.895★</b> (Drop of <b>-0.194★</b>).", bullet_style))
    story.append(Paragraph("• <b>Statistical Significance:</b> Welch's two-sample t-test: <b>t = 3.38 (p = 0.0008)</b>; Kolmogorov-Smirnov test: <b>D = 0.201 (p = 0.0003)</b>.", bullet_style))
    story.append(Paragraph("• <b>Alignment with Ground Truth:</b> The 2016–17 displayed distribution (3.89★) closely matched the 2015 true HTML baseline (3.85★), "
                           "confirming that aggressive ceiling rounding had been eliminated.", bullet_style))

    story.append(Spacer(1, 10))

    # Section 6: Inferential Statistical Tests
    story.append(Paragraph("6. Summary of Inferential Statistical Tests", h1_style))

    stat_data = [
        [Paragraph("Hypothesis Test", table_header), Paragraph("Null vs Alternative", table_header), Paragraph("Test Statistic", table_header), Paragraph("p-Value", table_header), Paragraph("Effect Size / CI", table_header), Paragraph("Verdict", table_header)],
        [Paragraph("<b>Paired t-Test</b> (2015 Inflation)", table_cell), Paragraph("H₀: μ_diff = 0<br/>H₁: μ_diff &gt; 0", table_cell), Paragraph("t = 15.54", table_cell_bold), Paragraph("&lt; 10⁻¹⁵", table_cell_bold), Paragraph("d = 1.34<br/>(Large)", table_cell), Paragraph("<font color='#10b981'><b>Reject H₀</b></font>", table_cell)],
        [Paragraph("<b>Wilcoxon Signed-Rank</b>", table_cell), Paragraph("Non-parametric paired median test", table_cell), Paragraph("W = 0.00", table_cell_bold), Paragraph("&lt; 10⁻¹⁵", table_cell_bold), Paragraph("Rank biserial r = 1.0", table_cell), Paragraph("<font color='#10b981'><b>Reject H₀</b></font>", table_cell)],
        [Paragraph("<b>Bootstrap 95% CI</b>", table_cell), Paragraph("10,000 resamples of mean inflation", table_cell), Paragraph("Mean: +0.244", table_cell), Paragraph("N/A", table_cell), Paragraph("[+0.213, +0.275] stars", table_cell_bold), Paragraph("<font color='#10b981'><b>Statistically Solid</b></font>", table_cell)],
        [Paragraph("<b>Welch's t-Test</b> (Temporal Drop)", table_cell), Paragraph("H₀: μ_15 = μ_16-17<br/>H₁: μ_15 ≠ μ_16-17", table_cell), Paragraph("t = 3.38", table_cell_bold), Paragraph("0.0008", table_cell_bold), Paragraph("d = 0.36<br/>(Moderate)", table_cell), Paragraph("<font color='#10b981'><b>Reject H₀</b></font>", table_cell)],
        [Paragraph("<b>Kolmogorov-Smirnov</b>", table_cell), Paragraph("Distribution shape equality test", table_cell), Paragraph("D = 0.201", table_cell_bold), Paragraph("0.0003", table_cell_bold), Paragraph("Shift in CDF shape", table_cell), Paragraph("<font color='#10b981'><b>Reject H₀</b></font>", table_cell)],
    ]
    stat_table = Table(stat_data, colWidths=[100, 105, 75, 60, 95, 69])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(stat_table)

    story.append(Spacer(1, 14))

    # Section 7: Technical Architecture & Code Structure
    story.append(Paragraph("7. Project Architecture & Codebase Structure", h1_style))
    story.append(Paragraph(
        "The project is structured with production modularity, automated test coverage, and clean separation of concerns:",
        body_style
    ))

    code_struct = [
        [Paragraph("Module / File", table_header), Paragraph("Responsibility & Key Capabilities", table_header)],
        [Paragraph("<code>src/data_loader.py</code>", table_cell_bold), Paragraph("Ingests and validates CSV datasets (2015 comparison, scrape, 2016-17), extracts film years safely, parses numeric columns.", table_cell)],
        [Paragraph("<code>src/analysis.py</code>", table_cell_bold), Paragraph("Computes discrepancy frequencies, cross-platform stats, continuous 101-point Gaussian KDE curves, and temporal comparisons.", table_cell)],
        [Paragraph("<code>src/statistics.py</code>", table_cell_bold), Paragraph("Inferential engine executing paired t-tests, Wilcoxon signed-rank, Welch's t-test, Kolmogorov-Smirnov, Cohen's d, and 10k bootstrap CI.", table_cell)],
        [Paragraph("<code>src/database.py</code>", table_cell_bold), Paragraph("In-memory SQLite database manager supporting safe read-only SQL queries across <code>fandango_2015</code>, <code>fandango_scrape</code>, <code>movie_ratings_16_17</code>.", table_cell)],
        [Paragraph("<code>app/main.py</code>", table_cell_bold), Paragraph("FastAPI ASGI backend serving JSON REST API endpoints (<code>/api/overview</code>, <code>/api/movies</code>, <code>/api/sql</code>, etc.) and web dashboard.", table_cell)],
        [Paragraph("<code>app/templates/index.html</code>", table_cell_bold), Paragraph("Modern Bento Grid UI featuring glitch simulator, interactive parity plot, spotlight film card, and filter chips.", table_cell)],
        [Paragraph("<code>tests/</code> (24 pytest tests)", table_cell_bold), Paragraph("Comprehensive automated test suite validating schemas, ranges, math formulas, statistical p-values, and API endpoints.", table_cell)],
        [Paragraph("<code>vercel.json</code> & <code>api/index.py</code>", table_cell_bold), Paragraph("Vercel serverless deployment configuration for 1-click global cloud deployment.", table_cell)],
    ]
    struct_table = Table(code_struct, colWidths=[150, 354])
    struct_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(struct_table)

    story.append(PageBreak())

    # Section 8: Presentation & Pitch Cheat-Sheet
    story.append(Paragraph("8. Project Presentation & Interview Pitch Guide", h1_style))
    story.append(Paragraph(
        "Use this cheat-sheet to explain the project with clarity and confidence during presentations, interviews, or reviews:",
        body_style
    ))

    # 30-Second Pitch Box
    story.append(Paragraph("<b>🎤 30-Second Elevator Pitch:</b>", h2_style))
    p30_text = (
        "<i>'I built v_rate_movies, an end-to-end data analytics application investigating movie rating bias on Fandango. "
        "By comparing displayed star ratings with underlying HTML values across 146 theatrical releases, I proved that 89% of movies "
        "were artificially inflated due to an aggressive ceiling-rounding algorithm (p &lt; 10⁻¹⁵). I packaged this analysis into a "
        "modern Bento Grid web application with interactive simulators, SQLite querying, and verified with 24 automated unit tests.'</i>"
    )
    p30_table = Table([[Paragraph(p30_text, callout_style)]], colWidths=[504])
    p30_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_subtle),
        ('BOX', (0,0), (-1,-1), 1, c_primary),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(p30_table)
    story.append(Spacer(1, 10))

    # 2-Minute Structured Walkthrough
    story.append(Paragraph("<b>📋 2-Minute Structured Walkthrough (5 Key Points):</b>", h2_style))
    story.append(Paragraph("<b>1. The Problem:</b> Fandango is an online ticket broker with an inherent conflict of interest. Higher ratings drive ticket conversions.", bullet_style))
    story.append(Paragraph("<b>2. The Discovery:</b> In 2015, Walt Hickey scraped raw HTML ratings and found they were consistently lower than the stars shown on screen.", bullet_style))
    story.append(Paragraph("<b>3. The Mathematics:</b> Fandango's frontend didn't use standard half-rounding; any fractional value &ge; 0.1 pushed a movie to the next half star (e.g. 4.1 &rarr; 4.5★).", bullet_style))
    story.append(Paragraph("<b>4. The Temporal Proof:</b> In 2016–17 follow-up data, displayed ratings dropped by ~0.20 stars (p = 0.0008), proving Fandango altered their algorithm after public exposure.", bullet_style))
    story.append(Paragraph("<b>5. The Engineering:</b> I engineered a clean Python analytics backend, automated statistical tests with SciPy/NumPy, and built a SaaS-grade Bento UI deployed to Vercel.", bullet_style))

    story.append(Spacer(1, 10))

    # Anticipated Q&A
    story.append(Paragraph("<b>❓ Anticipated Technical Q&A:</b>", h2_style))
    story.append(Paragraph("<b>Q: How did you prove the inflation was not random noise?</b><br/>"
                           "<b>A:</b> I conducted a paired Student's t-test on the differences (Displayed − HTML), yielding t = 15.54 (p &lt; 10⁻¹⁵) and Cohen's d = 1.34. "
                           "A 10,000-resample bootstrap confirmed a 95% confidence interval of [+0.213, +0.275] stars, entirely excluding zero.", bullet_style))
    story.append(Paragraph("<b>Q: Why did you use Kernel Density Estimation (KDE) instead of simple histograms?</b><br/>"
                           "<b>A:</b> Discrete star ratings suffer from binning artifacts in histograms. Continuous Gaussian KDE with optimal bandwidth provides "
                           "a smooth probability density function, clearly visualizing the rightward distribution shift and lack of sub-3.0 star ratings.", bullet_style))
    story.append(Paragraph("<b>Q: How is the project deployed?</b><br/>"
                           "<b>A:</b> It is configured for 1-click serverless deployment on Vercel using an ASGI FastAPI bridge (<code>api/index.py</code>) and runs locally via <code>run.bat</code> or <code>python -m app.main</code>.", bullet_style))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("<b>Project Links:</b> GitHub: <u>https://github.com/vartiwa/v_rate_movies</u> • Author: vartiwa", meta_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
