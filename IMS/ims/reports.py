"""
IMS - PDF Report Generator
Generates professional PDF reports using ReportLab.
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Brand colours ──────────────────────────────────────────
PRIMARY   = colors.HexColor('#1A5276')
ACCENT    = colors.HexColor('#2E86C1')
LIGHT_BG  = colors.HexColor('#D6EAF8')
SUCCESS   = colors.HexColor('#1E8449')
WARNING   = colors.HexColor('#D4AC0D')
DANGER    = colors.HexColor('#C0392B')
GREY      = colors.HexColor('#7F8C8D')
DARK_GREY = colors.HexColor('#2C3E50')
WHITE     = colors.white
LIGHT_ROW = colors.HexColor('#EBF5FB')

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=18,
                                textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica', fontSize=11,
                                   textColor=GREY, alignment=TA_CENTER, spaceAfter=2),
        'section': ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=PRIMARY, spaceBefore=12, spaceAfter=4),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=9,
                               textColor=DARK_GREY, spaceAfter=2),
        'right': ParagraphStyle('right', fontName='Helvetica', fontSize=9,
                                textColor=GREY, alignment=TA_RIGHT),
        'stat_label': ParagraphStyle('stat_label', fontName='Helvetica', fontSize=8,
                                     textColor=GREY, alignment=TA_CENTER),
        'stat_value': ParagraphStyle('stat_value', fontName='Helvetica-Bold', fontSize=16,
                                     textColor=PRIMARY, alignment=TA_CENTER),
    }


def _header_footer(canvas, doc, title):
    canvas.saveState()
    w, h = doc.pagesize
    # Header bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, h - 1.5*cm, w, 1.5*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont('Helvetica-Bold', 13)
    canvas.drawString(1*cm, h - 1.0*cm, 'IMS — Electronics Inventory Management System')
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(w - 1*cm, h - 1.0*cm, title)
    # Footer
    canvas.setFillColor(LIGHT_BG)
    canvas.rect(0, 0, w, 0.8*cm, fill=1, stroke=0)
    canvas.setFillColor(GREY)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1*cm, 0.25*cm, f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}")
    canvas.drawRightString(w - 1*cm, 0.25*cm, f"Page {doc.page}")
    canvas.restoreState()


def _table_style(header_color=PRIMARY, alt_row=LIGHT_ROW):
    return TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  header_color),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  8),
        ('TOPPADDING',    (0, 0), (-1, 0),  8),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING',    (0, 1), (-1, -1), 5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, alt_row]),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ])


def _summary_box(items, page_width):
    """Renders a row of KPI boxes: [(label, value, color), ...]"""
    n = len(items)
    col_w = (page_width - 2*cm) / n
    data = [[Paragraph(v, ParagraphStyle('sv', fontName='Helvetica-Bold',
                                          fontSize=14, textColor=c, alignment=TA_CENTER))
             for _, v, c in items],
            [Paragraph(lbl, ParagraphStyle('sl', fontName='Helvetica', fontSize=8,
                                            textColor=GREY, alignment=TA_CENTER))
             for lbl, _, _ in items]]
    t = Table(data, colWidths=[col_w]*n)
    t.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('LINEAFTER',     (0, 0), (-2, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND',    (0, 0), (-1, -1), LIGHT_BG),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


# ════════════════════════════════════════════════════════════════════════
#  1. SALES REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_sales_report(rows, start_date, end_date, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1*cm, rightMargin=1*cm)
    S = _styles()
    story = []

    story.append(Paragraph("SALES REPORT", S['title']))
    story.append(Paragraph(f"Period: {start_date}  to  {end_date}", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    # KPI summary
    total_revenue = sum(r['total_amount'] for r in rows)
    total_orders  = len(rows)
    avg_order     = total_revenue / total_orders if total_orders else 0
    summary = [
        ("Total Orders",   str(total_orders),         PRIMARY),
        ("Total Revenue",  f"KES {total_revenue:,.2f}", SUCCESS),
        ("Avg Order Value",f"KES {avg_order:,.2f}",    ACCENT),
    ]
    pw = landscape(A4)[0] - 2*cm
    story.append(_summary_box(summary, pw + 2*cm))
    story.append(Spacer(1, 14))

    # Table
    headers = ['Order No.', 'Date', 'Customer', 'Staff', 'Amount (KES)', 'Status']
    data = [headers]
    for r in rows:
        data.append([
            r['order_number'],
            r['created_at'][:16],
            r.get('customer', '') or 'Walk-in',
            r.get('staff', '') or '—',
            f"{r['total_amount']:,.2f}",
            r['status'],
        ])

    col_widths = [3.5*cm, 3.8*cm, 5*cm, 4.5*cm, 3.5*cm, 2.8*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style()
    # Colour status column
    for i, r in enumerate(rows, start=1):
        col = SUCCESS if r['status'] == 'Completed' else WARNING
        ts.add('TEXTCOLOR', (5, i), (5, i), col)
        ts.add('FONTNAME',  (5, i), (5, i), 'Helvetica-Bold')
    # Right-align amount column
    ts.add('ALIGN', (4, 0), (4, -1), 'RIGHT')
    t.setStyle(ts)
    story.append(t)

    # Total row
    story.append(Spacer(1, 6))
    total_row = Table(
        [[Paragraph(f"TOTAL REVENUE: KES {total_revenue:,.2f}",
                    ParagraphStyle('tr', fontName='Helvetica-Bold', fontSize=10,
                                   textColor=PRIMARY, alignment=TA_RIGHT))]],
        colWidths=[sum(col_widths)]
    )
    total_row.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(total_row)

    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Sales Report"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Sales Report"))
    return filename


# ════════════════════════════════════════════════════════════════════════
#  2. INVENTORY STATUS REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_inventory_report(rows, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1*cm, rightMargin=1*cm)
    S = _styles()
    story = []

    story.append(Paragraph("INVENTORY STATUS REPORT", S['title']))
    story.append(Paragraph(f"As of: {datetime.now().strftime('%d %B %Y')}", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    total_items  = len(rows)
    in_stock     = sum(1 for r in rows if r['stock_status'] == 'In Stock')
    low_stock    = sum(1 for r in rows if r['stock_status'] == 'Low Stock')
    out_of_stock = sum(1 for r in rows if r['stock_status'] == 'Out of Stock')
    total_value  = sum(r['stock_value'] for r in rows)

    pw = landscape(A4)[0]
    summary = [
        ("Total SKUs",    str(total_items),          PRIMARY),
        ("In Stock",      str(in_stock),              SUCCESS),
        ("Low Stock",     str(low_stock),             WARNING),
        ("Out of Stock",  str(out_of_stock),          DANGER),
        ("Total Value",   f"KES {total_value:,.2f}", ACCENT),
    ]
    story.append(_summary_box(summary, pw))
    story.append(Spacer(1, 14))

    headers = ['Code', 'Product Name', 'Category', 'Qty', 'Reorder Lvl', 'Unit Price', 'Stock Value', 'Status', 'Expiry']
    data = [headers]
    for r in rows:
        data.append([
            r['productcode'],
            r['name'],
            r.get('category') or '—',
            str(r['quantity']),
            str(r['reorder_level']),
            f"KES {r['unit_price']:,.2f}",
            f"KES {r['stock_value']:,.2f}",
            r['stock_status'],
            r.get('expiry_date') or '—',
        ])

    col_widths = [2.2*cm, 5.5*cm, 3*cm, 1.5*cm, 2*cm, 2.8*cm, 3*cm, 2.5*cm, 2.5*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style()
    status_colors = {'In Stock': SUCCESS, 'Low Stock': WARNING, 'Out of Stock': DANGER}
    for i, r in enumerate(rows, start=1):
        col = status_colors.get(r['stock_status'], GREY)
        ts.add('TEXTCOLOR', (7, i), (7, i), col)
        ts.add('FONTNAME',  (7, i), (7, i), 'Helvetica-Bold')
        if r['stock_status'] != 'In Stock':
            ts.add('BACKGROUND', (0, i), (-1, i),
                   colors.HexColor('#FEF9E7') if r['stock_status'] == 'Low Stock'
                   else colors.HexColor('#FDEDEC'))
    ts.add('ALIGN', (3,0), (6,-1), 'RIGHT')
    t.setStyle(ts)
    story.append(t)

    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Inventory Report"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Inventory Report"))
    return filename


# ════════════════════════════════════════════════════════════════════════
#  3. TOP-SELLING PRODUCTS REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_top_products_report(rows, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"top_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = _styles()
    story = []

    story.append(Paragraph("TOP SELLING PRODUCTS REPORT", S['title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=14))

    total_revenue = sum(r['total_revenue'] for r in rows)
    headers = ['Rank', 'Product Code', 'Product Name', 'Category', 'Units Sold', 'Revenue (KES)']
    data = [headers]
    for i, r in enumerate(rows, 1):
        data.append([
            str(i),
            r['productcode'] or '—',
            r['name'] or 'Unknown',
            r.get('category') or '—',
            str(r['total_sold']),
            f"{r['total_revenue']:,.2f}",
        ])

    col_widths = [1.2*cm, 3*cm, 6*cm, 3.5*cm, 2.5*cm, 3.5*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style()
    # Gold/silver/bronze for top 3
    medal_colors = [colors.HexColor('#F9E79F'), colors.HexColor('#D5D8DC'), colors.HexColor('#EDBB99')]
    for i in range(min(3, len(rows))):
        ts.add('BACKGROUND', (0, i+1), (-1, i+1), medal_colors[i])
    ts.add('ALIGN', (4,0), (5,-1), 'RIGHT')
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Total Revenue from Listed Products: KES {total_revenue:,.2f}",
                            ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=10,
                                           textColor=PRIMARY, alignment=TA_RIGHT)))

    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Top Products Report"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Top Products Report"))
    return filename


# ════════════════════════════════════════════════════════════════════════
#  4. CUSTOMER REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_customer_report(rows, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"customer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = _styles()
    story = []

    story.append(Paragraph("CUSTOMER PURCHASE REPORT", S['title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=14))

    total_customers = len(rows)
    total_revenue   = sum(r['total_spent'] for r in rows)
    active_customers = sum(1 for r in rows if r['total_orders'] > 0)

    pw = A4[0]
    summary = [
        ("Total Customers", str(total_customers),       PRIMARY),
        ("Active Customers",str(active_customers),      SUCCESS),
        ("Total Revenue",   f"KES {total_revenue:,.2f}", ACCENT),
    ]
    story.append(_summary_box(summary, pw))
    story.append(Spacer(1, 14))

    headers = ['Customer Name', 'Phone', 'Email', 'Total Orders', 'Total Spent (KES)']
    data = [headers]
    for r in rows:
        data.append([
            r['fullname'],
            r.get('phone') or '—',
            r.get('email') or '—',
            str(r['total_orders']),
            f"{r['total_spent']:,.2f}",
        ])

    col_widths = [5*cm, 3*cm, 5.5*cm, 2.5*cm, 3.5*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style()
    ts.add('ALIGN', (3,0), (4,-1), 'RIGHT')
    t.setStyle(ts)
    story.append(t)

    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Customer Report"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Customer Report"))
    return filename


# ════════════════════════════════════════════════════════════════════════
#  5. PURCHASE REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_purchase_report(rows, start_date, end_date, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"purchase_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1*cm, rightMargin=1*cm)
    S = _styles()
    story = []

    story.append(Paragraph("PURCHASE REPORT", S['title']))
    story.append(Paragraph(f"Period: {start_date}  to  {end_date}", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    total_spend = sum(r['total_amount'] for r in rows)
    summary = [
        ("Total Purchases", str(len(rows)),              PRIMARY),
        ("Total Spend",     f"KES {total_spend:,.2f}",   DANGER),
    ]
    pw = landscape(A4)[0]
    story.append(_summary_box(summary, pw))
    story.append(Spacer(1, 14))

    headers = ['Purchase No.', 'Date', 'Supplier', 'Staff', 'Amount (KES)', 'Status']
    data = [headers]
    for r in rows:
        data.append([
            r['purchase_number'],
            r['created_at'][:16],
            r.get('supplier_name') or '—',
            r.get('staff_name') or '—',
            f"{r['total_amount']:,.2f}",
            r['status'],
        ])

    col_widths = [3.8*cm, 3.8*cm, 6*cm, 4.5*cm, 3.5*cm, 2.8*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style(header_color=colors.HexColor('#922B21'))
    ts.add('ALIGN', (4,0), (4,-1), 'RIGHT')
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 6))
    story.append(Paragraph(f"TOTAL SPEND: KES {total_spend:,.2f}",
                            ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=10,
                                           textColor=DANGER, alignment=TA_RIGHT)))
    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Purchase Report"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Purchase Report"))
    return filename


# ════════════════════════════════════════════════════════════════════════
#  6. LOW STOCK ALERT REPORT
# ════════════════════════════════════════════════════════════════════════
def generate_low_stock_report(rows, filename=None):
    if not filename:
        filename = os.path.join(REPORTS_DIR, f"low_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            topMargin=2*cm, bottomMargin=1.2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = _styles()
    story = []

    story.append(Paragraph("LOW STOCK ALERT REPORT", S['title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}", S['subtitle']))
    story.append(Paragraph("⚠ Action Required: The following products need restocking.", S['section']))
    story.append(HRFlowable(width="100%", thickness=2, color=WARNING, spaceAfter=10))

    headers = ['Code', 'Product Name', 'Category', 'Current Qty', 'Reorder Level', 'Shortage', 'Unit Price']
    data = [headers]
    for r in rows:
        shortage = max(0, r['reorder_level'] - r['quantity'])
        data.append([
            r['productcode'],
            r['name'],
            r.get('category_name') or '—',
            str(r['quantity']),
            str(r['reorder_level']),
            str(shortage),
            f"KES {r['unit_price']:,.2f}",
        ])

    col_widths = [2.5*cm, 5.5*cm, 3*cm, 2.5*cm, 2.8*cm, 2.5*cm, 3*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = _table_style(header_color=WARNING)
    ts.add('TEXTCOLOR', (0, 0), (-1, 0), DARK_GREY)
    for i, r in enumerate(rows, 1):
        if r['quantity'] <= 0:
            ts.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FDEDEC'))
            ts.add('TEXTCOLOR', (3, i), (3, i), DANGER)
            ts.add('FONTNAME',  (3, i), (3, i), 'Helvetica-Bold')
    ts.add('ALIGN', (3,0), (-1,-1), 'CENTER')
    t.setStyle(ts)
    story.append(t)

    doc.build(story, onFirstPage=lambda c, d: _header_footer(c, d, "Low Stock Alert"),
              onLaterPages=lambda c, d: _header_footer(c, d, "Low Stock Alert"))
    return filename
