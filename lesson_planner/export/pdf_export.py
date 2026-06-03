"""Render a DailySchedule to a classroom-ready PDF poster using QPainter.

All layout is done in device pixels (printer.resolution() DPI).
Font sizes are set via setPixelSize() so they match physical inches exactly.
"""
from datetime import date, time
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QMarginsF, QPointF
from PySide6.QtGui import (
    QPainter, QFont, QColor, QPen, QBrush, QPainterPath,
    QPageSize, QPageLayout,
)
from PySide6.QtPrintSupport import QPrinter

from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.gui.colors import bg_for_domain, border_for_domain


def _fmt_time(t: time) -> str:
    hour = t.hour % 12 or 12
    suffix = "AM" if t.hour < 12 else "PM"
    return f"{hour}:{t.minute:02d} {suffix}"


def _px(points: float, dpi: int) -> float:
    """Convert typographic points to device pixels."""
    return points * dpi / 72.0


def _font(family: str, pt: float, dpi: int, bold: bool = False, italic: bool = False) -> QFont:
    f = QFont(family)
    f.setPixelSize(max(1, int(_px(pt, dpi))))
    f.setBold(bold)
    f.setItalic(italic)
    return f


def _rounded_rect(painter: QPainter, rect: QRectF, radius: float,
                  fill: QColor, stroke: QColor, stroke_w: float):
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    painter.fillPath(path, QBrush(fill))
    painter.setPen(QPen(stroke, stroke_w))
    painter.drawPath(path)


def export_pdf(schedule: DailySchedule, output_path: Path) -> None:
    """Write the schedule to a classroom-ready PDF poster."""
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(str(output_path))
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    # Ask for no extra margins; printer will apply its own minimum hardware margins.
    printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)

    painter = QPainter()
    if not painter.begin(printer):
        raise RuntimeError(f"Could not open PDF for writing: {output_path}")
    try:
        dpi = printer.resolution()
        page = printer.pageRect(QPrinter.Unit.DevicePixel)
        W = page.width()
        H = page.height()
        _draw_page(painter, printer, schedule, dpi, W, H)
    finally:
        painter.end()


def _draw_page(painter: QPainter, printer: QPrinter,
               schedule: DailySchedule, dpi: int, W: float, H: float):

    # ── Layout constants (all in typographic points, converted via _px) ───────
    margin     = _px(36, dpi)     # 0.5-inch inner margin
    time_col   = _px(48, dpi)     # width of left time-badge column
    bar_w      = _px(5, dpi)      # coloured accent bar width
    icon_col   = _px(18, dpi)     # emoji column width
    pad        = _px(7, dpi)      # inner card top/bottom padding
    card_h     = _px(34, dpi)     # total card height
    gap        = _px(5, dpi)      # gap between cards
    radius     = _px(5, dpi)      # card corner radius

    content_w = W - 2 * margin
    y = margin

    def new_page():
        nonlocal y
        printer.newPage()
        y = margin

    # ── Header ───────────────────────────────────────────────────────────────
    line_h_sm = _px(11, dpi)
    line_h_lg = _px(24, dpi)

    painter.setFont(_font("Arial", 9, dpi, italic=True))
    painter.setPen(QColor("#888888"))
    painter.drawText(QPointF(margin, y + line_h_sm), "Playful Pathway Planner")
    y += line_h_sm + _px(4, dpi)

    painter.setFont(_font("Arial", 20, dpi, bold=True))
    painter.setPen(QColor("#2c3e50"))
    painter.drawText(QPointF(margin, y + line_h_lg), schedule.name)
    y += line_h_lg + _px(6, dpi)

    today = date.today().strftime("%B %d, %Y")
    total = schedule.total_minutes
    h, m = divmod(total, 60)
    total_str = f"{h}h {m}min" if h else f"{total} min"
    meta = (
        f"{today}  •  Starts {_fmt_time(schedule.start_time)}"
        f"  •  {len(schedule.blocks)} activities  •  {total_str} total"
    )
    painter.setFont(_font("Arial", 9, dpi))
    painter.setPen(QColor("#555555"))
    painter.drawText(QPointF(margin, y + line_h_sm), meta)
    y += line_h_sm + _px(6, dpi)

    painter.setPen(QPen(QColor("#cccccc"), _px(0.75, dpi)))
    painter.drawLine(
        QPointF(margin, y), QPointF(margin + content_w, y)
    )
    y += _px(8, dpi)

    # ── Activity blocks ───────────────────────────────────────────────────────
    stroke_w = _px(1.0, dpi)

    for i, block in enumerate(schedule.blocks):
        act = block.activity
        start_t = schedule.block_start_time(i)
        bg_color = QColor(bg_for_domain(act.domain))
        border_color = QColor(border_for_domain(act.domain))

        if y + card_h > H - margin - _px(14, dpi):
            new_page()

        # Time badge (right-aligned, vertically centred)
        badge_rect = QRectF(margin, y, time_col - _px(6, dpi), card_h)
        painter.setFont(_font("Arial", 8, dpi, bold=True))
        painter.setPen(QColor("#444444"))
        painter.drawText(badge_rect, Qt.AlignRight | Qt.AlignVCenter, _fmt_time(start_t))

        # Card background + border
        card_x = margin + time_col
        card_w = content_w - time_col
        card_rect = QRectF(card_x, y, card_w, card_h)
        _rounded_rect(painter, card_rect, radius, bg_color, border_color, stroke_w)

        # Accent bar on left edge of card
        bar_rect = QRectF(card_x, y + _px(3, dpi), bar_w, card_h - _px(6, dpi))
        bar_path = QPainterPath()
        bar_path.addRoundedRect(bar_rect, _px(2.5, dpi), _px(2.5, dpi))
        painter.fillPath(bar_path, QBrush(border_color))

        # Emoji icon
        icon_x = card_x + bar_w + _px(6, dpi)
        icon_rect = QRectF(icon_x, y, icon_col, card_h)
        painter.setFont(_font("Noto Color Emoji,Segoe UI Emoji,Apple Color Emoji", 13, dpi))
        painter.setPen(QColor("#111111"))
        painter.drawText(icon_rect, Qt.AlignHCenter | Qt.AlignVCenter, act.icon)

        # Title (upper area of card)
        text_x = icon_x + icon_col + _px(4, dpi)
        text_w = card_w - bar_w - _px(6, dpi) - icon_col - _px(4, dpi) - _px(6, dpi)
        title_h = _px(13, dpi)
        title_rect = QRectF(text_x, y + pad, text_w, title_h)
        painter.setFont(_font("Arial", 11, dpi, bold=True))
        painter.setPen(QColor("#111111"))
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, act.title)

        # Domain + duration (lower area of card)
        meta_h = _px(10, dpi)
        meta_rect = QRectF(text_x, y + card_h - pad - meta_h, text_w, meta_h)
        painter.setFont(_font("Arial", 8, dpi))
        painter.setPen(QColor("#444444"))
        painter.drawText(
            meta_rect, Qt.AlignLeft | Qt.AlignVCenter,
            f"{act.domain}  •  {block.duration} min",
        )

        y += card_h + gap

    # ── Footer ────────────────────────────────────────────────────────────────
    painter.setFont(_font("Arial", 7, dpi, italic=True))
    painter.setPen(QColor("#bbbbbb"))
    painter.drawText(
        QPointF(margin, H - _px(6, dpi)),
        "Created with Playful Pathway Planner",
    )
