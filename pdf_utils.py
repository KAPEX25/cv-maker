# -*- coding: utf-8 -*-
"""
pdf_utils.py
CV PDF üretimi için ortak yardımcı fonksiyonlar:
- Metin sarma (word wrap)
- Sayfa taşması (page break) yönetimi
- Basit çizim yardımcıları (yuvarlatılmış kutu, çizgi, madde imi)
"""

import os
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

PAGE_W, PAGE_H = A4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")

# Türkçe karakterleri (ğ, ş, ı, İ, ö, ü, ç) tam destekleyen font ailesi.
# reportlab'ın dahili Helvetica fontu bu karakterleri desteklemediği için
# DejaVu Sans gömülü olarak kullanılır.
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
FONT_ITALIC = "DejaVuSans-Oblique"
FONT_SERIF = "DejaVuSerif"
FONT_SERIF_BOLD = "DejaVuSerif-Bold"
FONT_MONO = "DejaVuSansMono"
FONT_MONO_BOLD = "DejaVuSansMono-Bold"

_fonts_registered = False


def register_fonts():
    """Türkçe karakter destekli fontları reportlab'a kaydeder (bir kez)."""
    global _fonts_registered
    if _fonts_registered:
        return
    pairs = [
        (FONT_REGULAR, "DejaVuSans.ttf"),
        (FONT_BOLD, "DejaVuSans-Bold.ttf"),
        (FONT_ITALIC, "DejaVuSans-Oblique.ttf"),
        (FONT_SERIF, "DejaVuSerif.ttf"),
        (FONT_SERIF_BOLD, "DejaVuSerif-Bold.ttf"),
        (FONT_MONO, "DejaVuSansMono.ttf"),
        (FONT_MONO_BOLD, "DejaVuSansMono-Bold.ttf"),
    ]
    for name, filename in pairs:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, filename)))
    _fonts_registered = True


def wrap_text(text, font_name, font_size, max_width):
    """Verilen metni max_width genişliğine sığacak şekilde satırlara böler."""
    if not text:
        return []
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if stringWidth(trial, font_name, font_size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            # Kelimenin kendisi satırdan uzunsa karakter bazlı böl
            if stringWidth(word, font_name, font_size) > max_width:
                chunk = ""
                for ch in word:
                    if stringWidth(chunk + ch, font_name, font_size) <= max_width:
                        chunk += ch
                    else:
                        lines.append(chunk)
                        chunk = ch
                current = chunk
            else:
                current = word
    if current:
        lines.append(current)
    return lines


class PageFlow:
    """
    Bir reportlab canvas nesnesi üzerinde, sayfa taşmasını otomatik
    yöneten basit bir akış (flow) yardımcı sınıfı.

    on_new_page(canvas, page_index): yeni sayfa açıldığında arka planı /
    başlığı / kenar çubuğunu yeniden çizmek için çağrılır ve içerik
    başlangıcı için (x, y, max_width) döndürmelidir. None dönerse
    varsayılan margin kullanılır.
    """

    def __init__(self, canvas, bottom_margin=45, on_new_page=None):
        self.c = canvas
        self.bottom_margin = bottom_margin
        self.on_new_page = on_new_page
        self.page_index = 1

    def ensure_space(self, y, needed_height, x=None, max_width=None):
        """y konumunda needed_height kadar yer yoksa yeni sayfa açar,
        yeni y (ve varsa x, max_width) döndürür."""
        if y - needed_height < self.bottom_margin:
            self.c.showPage()
            self.page_index += 1
            if self.on_new_page:
                nx, ny, nmw = self.on_new_page(self.c, self.page_index)
                if x is not None:
                    return ny, nx, nmw
                return ny
            else:
                return PAGE_H - 60
        return y

    def draw_paragraph(self, text, x, y, max_width, font_name, font_size,
                        leading, color=HexColor("#222222"), align="left"):
        """Bir metni sarıp, sayfa taşmasını kontrol ederek satır satır çizer.
        Döndürülen değer: (yeni_y, yeni_x, yeni_max_width)"""
        lines = wrap_text(text, font_name, font_size, max_width)
        cur_x, cur_mw = x, max_width
        for line in lines:
            res = self.ensure_space(y, leading, x=cur_x, max_width=cur_mw)
            if isinstance(res, tuple):
                y, cur_x, cur_mw = res
            else:
                y = res
            self.c.setFont(font_name, font_size)
            self.c.setFillColor(color)
            if align == "right":
                self.c.drawRightString(cur_x + cur_mw, y, line)
            elif align == "center":
                self.c.drawCentredString(cur_x + cur_mw / 2, y, line)
            else:
                self.c.drawString(cur_x, y, line)
            y -= leading
        return y, cur_x, cur_mw


def draw_rounded_box(c, x, y, w, h, radius, fill_color, stroke_color=None):
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke_color else 0, fill=1)


def draw_bullet_dot(c, x, y, color, r=1.8):
    c.setFillColor(color)
    c.circle(x, y, r, stroke=0, fill=1)


def draw_hline(c, x1, x2, y, color, width=0.8):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)


def initials(name):
    parts = [p for p in str(name).split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()
