# -*- coding: utf-8 -*-
"""
templates.py
CV verisini alıp 10 farklı görsel tasarımda PDF olarak üreten fonksiyonlar.

Her şablon fonksiyonu imzası:
    def draw_xxx(canvas, data) -> None
canvas zaten oluşturulmuş bir reportlab.pdfgen.canvas.Canvas nesnesidir,
fonksiyon çizimini yapar ancak canvas.save() çağırmaz (bunu app.py yapar).
"""

from urllib.parse import quote

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4

from pdf_utils import (
    PAGE_W, PAGE_H, wrap_text, PageFlow, draw_rounded_box,
    draw_bullet_dot, draw_hline, initials,
    FONT_REGULAR, FONT_BOLD, FONT_ITALIC, FONT_SERIF, FONT_SERIF_BOLD,
    FONT_MONO, FONT_MONO_BOLD, register_fonts,
)

register_fonts()


# --------------------------------------------------------------------------
# Ortak yardımcılar
# --------------------------------------------------------------------------

# İki dilli bölüm başlıkları
SECTION_TITLES = {
    "tr": {
        "summary": "Profil Özeti",
        "experience": "İş Deneyimi",
        "education": "Eğitim",
        "skills": "Yetenekler",
        "languages": "Diller",
        "certifications": "Sertifikalar",
        "contact": "İletişim",
        "present": "Devam ediyor",
    },
    "en": {
        "summary": "Professional Summary",
        "experience": "Work Experience",
        "education": "Education",
        "skills": "Skills",
        "languages": "Languages",
        "certifications": "Certifications",
        "contact": "Contact",
        "present": "Present",
    },
}


def _t(data, key):
    """data['language'] değerine göre bölüm başlığını döndürür."""
    lang = data.get("language", "tr")
    return SECTION_TITLES.get(lang, SECTION_TITLES["tr"]).get(key, key)


def _g(data, key, default=""):
    v = data.get(key, default)
    if v:
        return v
    if key == "full_name":
        return "Ad Soyad" if data.get("language", "tr") == "tr" else "Full Name"
    return default


def _absolute_url(value):
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    return "https://" + value


def _encode_url(url):
    """URL'nin path kısmındaki Türkçe/özel karakterleri percent-encode eder.
    Örn: 'mete-ç' -> 'mete-%C3%A7' (PDF linkURL için gerekli)"""
    if not url:
        return url
    for scheme in ("https://", "http://"):
        if url.startswith(scheme):
            rest = url[len(scheme):]
            if "/" in rest:
                host, path = rest.split("/", 1)
                return scheme + host + "/" + quote(path, safe="/:@-._~!$&'()*+,;=%")
            return scheme + rest
    return url


def contact_items(data):
    """İletişim öğelerini (görünen_metin, url) çiftleri olarak döndürür.
    LinkedIn / GitHub / Web sitesi için url dolu gelir ve PDF'te
    tıklanabilir link olarak çizilir."""
    items = []
    if data.get("phone"):
        items.append((data["phone"], None))
    if data.get("email"):
        items.append((data["email"], None))
    if data.get("address"):
        items.append((data["address"], None))
    if data.get("linkedin"):
        v = data["linkedin"].strip()
        url = _absolute_url(v)
        if "linkedin.com" not in v and not v.startswith("www."):
            url = "https://www.linkedin.com/" + v.lstrip("/")
        items.append(("LinkedIn", _encode_url(url)))
    if data.get("github"):
        v = data["github"].strip()
        url = _absolute_url(v)
        if "github.com" not in v and not v.startswith("www."):
            url = "https://github.com/" + v.lstrip("/")
        items.append(("GitHub", _encode_url(url)))
    if data.get("website"):
        v = data["website"].strip()
        url = _absolute_url(v)
        display = v.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]
        items.append((display if display else "Website", _encode_url(url)))
    return items


def _draw_contact_item(c, label, url, x, y, max_w, font, size, color, leading=None):
    """Tek bir iletişim öğesini (muhtemelen çok satır) çizer; url varsa
    tıklanabilir link ve alt çizgi ekler. Son satırın altındaki y döner."""
    leading = leading or size * 1.4
    for line in wrap_text(label, font, size, max_w):
        c.setFont(font, size)
        c.setFillColor(color)
        c.drawString(x, y, line)
        if url:
            w = c.stringWidth(line, font, size)
            c.linkURL(url, (x, y - 1, x + w, y + size), relative=0)
            c.setStrokeColor(color)
            c.setLineWidth(0.5)
            c.line(x, y - 1, x + w, y - 1)
        y -= leading
    return y


def draw_contact_line(c, data, x, y, max_w, font, size, color, separator="   •   ",
                      align="left", leading=None):
    """İletişim öğelerini tek satıra / gerekirse çok satıra sararak çizer.
    LinkedIn / GitHub / Web sitesi metinleri tıklanabilir link olur."""
    items = contact_items(data)
    if not items:
        return y
    leading = leading or size * 1.4
    sep_w = c.stringWidth(separator, font, size)

    # satırlara böl
    lines = []
    cur = []
    cur_w = 0
    for label, url in items:
        w = c.stringWidth(label, font, size)
        if cur and cur_w + sep_w + w > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
        if cur:
            cur_w += sep_w
        cur.append((label, url, w))
        cur_w += w
    if cur:
        lines.append(cur)

    for line in lines:
        total = sum(w for _, _, w in line) + sep_w * (len(line) - 1)
        if align == "center":
            cx = x + (max_w - total) / 2
        elif align == "right":
            cx = x + max_w - total
        else:
            cx = x
        for label, url, w in line:
            c.setFont(font, size)
            c.setFillColor(color)
            c.drawString(cx, y, label)
            if url:
                c.linkURL(url, (cx, y - 1, cx + w, y + (size * 1.2)), relative=0)
                c.setStrokeColor(color)
                c.setLineWidth(0.5)
                c.line(cx, y - 1, cx + w, y - 1)
            cx += w + sep_w
        y -= leading
    return y


def draw_wrapped_line(c, text, x, y, max_width, font, size, color, leading=None, align="left"):
    """Tek bir metni (ör. iletişim satırı) gerekirse birden fazla satıra
    sararak çizer ve son satırın altındaki y konumunu döndürür.
    Sayfa taşması kontrolü yapmaz; başlık alanında (sayfa 1 üstü) kullanılır."""
    leading = leading or size * 1.4
    lines = wrap_text(text, font, size, max_width)
    if not lines:
        return y
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        if align == "center":
            c.drawCentredString(x + max_width / 2, y, line)
        elif align == "right":
            c.drawRightString(x + max_width, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def date_range(item, language="tr"):
    s = item.get("start", "")
    e = item.get("end", "")
    if s or e:
        if e:
            return f"{s} - {e}"
        present = SECTION_TITLES.get(language, SECTION_TITLES["tr"])["present"]
        return f"{s} - {present}"
    return ""


def _lang(data):
    return data.get("language", "tr")


# --------------------------------------------------------------------------
# 1. KLASİK — sade siyah/beyaz, ortalanmış başlık
# --------------------------------------------------------------------------

def draw_classic(c, data):
    accent = HexColor("#222222")
    text_color = HexColor("#2b2b2b")
    muted = HexColor("#6b6b6b")
    margin = 55
    max_w = PAGE_W - 2 * margin
    y = PAGE_H - 65

    c.setFont(FONT_BOLD, 24)
    c.setFillColor(accent)
    c.drawCentredString(PAGE_W / 2, y, _g(data, "full_name"))
    y -= 22

    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 12.5)
        c.setFillColor(muted)
        c.drawCentredString(PAGE_W / 2, y, data["job_title"])
        y -= 18

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_REGULAR, 9, muted, separator="   •   ", align="center",
                              leading=12)
        y -= 4

    draw_hline(c, margin, PAGE_W - margin, y, accent, 1.1)
    y -= 22

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_BOLD, 12.5)
        c.setFillColor(accent)
        c.drawString(margin, y, title.upper())
        y -= 5
        draw_hline(c, margin, PAGE_W - margin, y, HexColor("#cccccc"), 0.7)
        return y - 14

    _sections_generic(
        c, flow, data, margin, max_w, y, heading,
        body_font=FONT_REGULAR, body_size=9.8, text_color=text_color,
        bold_font=FONT_BOLD, muted=muted, bullet_color=accent,
    )


def _plain_new_page(c, margin):
    return margin, PAGE_H - 60, PAGE_W - 2 * margin


def _sections_generic(c, flow, data, margin, max_w, y, heading_fn,
                       body_font, body_size, text_color, bold_font, muted,
                       bullet_color, leading=13.6, item_gap=8):
    """Summary / Experience / Education / Skills / Languages / Certifications
    bölümlerini tek sütun olarak sırayla çizen ortak akış."""
    lang = _lang(data)

    if data.get("summary"):
        y = heading_fn(_t(data, "summary"), y)
        y, _, _ = flow.draw_paragraph(data["summary"], margin, y, max_w,
                                       body_font, body_size, leading, text_color)
        y -= 8

    if data.get("experience"):
        y = heading_fn(_t(data, "experience"), y)
        for exp in data["experience"]:
            y = flow.ensure_space(y, 24)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(bold_font, 10.3)
            c.setFillColor(text_color)
            c.drawString(margin, y, _c or _p)
            dr = date_range(exp, lang)
            if dr:
                c.setFont(body_font, 8.7)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if _c and _p:
                c.setFont(FONT_ITALIC, 9.4)
                c.setFillColor(muted)
                c.drawString(margin, y, _p)
                y -= 12.5
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, leading)
                    draw_bullet_dot(c, margin + 3, y + 3, bullet_color)
                    y, _, _ = flow.draw_paragraph(line.strip(), margin + 10, y,
                                                   max_w - 10, body_font, body_size - 0.3,
                                                   leading, text_color)
            y -= item_gap

    if data.get("education"):
        y = heading_fn(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(bold_font, 10.3)
            c.setFillColor(text_color)
            c.drawString(margin, y, edu.get("degree", ""))
            dr = date_range(edu, lang)
            if dr:
                c.setFont(body_font, 8.7)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if edu.get("school"):
                c.setFont(FONT_ITALIC, 9.4)
                c.setFillColor(muted)
                c.drawString(margin, y, edu["school"])
                y -= 12.5
            if edu.get("description"):
                y, _, _ = flow.draw_paragraph(edu["description"], margin, y, max_w,
                                               body_font, body_size - 0.3, leading, text_color)
            y -= item_gap

    if data.get("skills"):
        y = heading_fn(_t(data, "skills"), y)
        y, _, _ = flow.draw_paragraph("  •  ".join(data["skills"]), margin, y, max_w,
                                       body_font, body_size, leading, text_color)
        y -= 8

    if data.get("languages"):
        y = heading_fn(_t(data, "languages"), y)
        y, _, _ = flow.draw_paragraph("  •  ".join(data["languages"]), margin, y, max_w,
                                       body_font, body_size, leading, text_color)
        y -= 8

    if data.get("certifications"):
        y = heading_fn(_t(data, "certifications"), y)
        for cert in data["certifications"]:
            y = flow.ensure_space(y, leading)
            draw_bullet_dot(c, margin + 3, y + 3, bullet_color)
            y, _, _ = flow.draw_paragraph(cert, margin + 10, y, max_w - 10,
                                           body_font, body_size, leading, text_color)
        y -= 8

    return y


# --------------------------------------------------------------------------
# 2. MODERN MAVİ — üstte renkli başlık bandı
# --------------------------------------------------------------------------

def draw_modern_blue(c, data):
    accent = HexColor("#1d5fae")
    dark = HexColor("#123a6e")
    text_color = HexColor("#28313c")
    muted = HexColor("#5c6773")
    margin = 55
    max_w = PAGE_W - 2 * margin

    citems = contact_items(data)
    band_h = 96 + 11 * len(citems)
    c.setFillColor(dark)
    c.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    c.setFillColor(accent)
    c.rect(0, PAGE_H - band_h - 5, PAGE_W, 5, stroke=0, fill=1)

    c.setFont(FONT_BOLD, 25)
    c.setFillColor(white)
    c.drawString(margin, PAGE_H - 52, _g(data, "full_name"))
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 13)
        c.setFillColor(HexColor("#d7e6fb"))
        c.drawString(margin, PAGE_H - 74, data["job_title"])

    if citems:
        cy = PAGE_H - 96
        for label, url in citems:
            cy = _draw_contact_item(c, label, url, margin, cy, max_w, FONT_REGULAR, 8.8,
                                    HexColor("#cfe0f7"), leading=11)

    y = PAGE_H - band_h - 28

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 22)
        draw_rounded_box(c, margin, y - 3, 4, 14, 2, accent)
        c.setFont(FONT_BOLD, 12.5)
        c.setFillColor(dark)
        c.drawString(margin + 10, y, title)
        return y - 16

    _sections_generic(c, flow, data, margin, max_w, y, heading,
                       body_font=FONT_REGULAR, body_size=9.8, text_color=text_color,
                       bold_font=FONT_BOLD, muted=muted, bullet_color=accent)


# --------------------------------------------------------------------------
# 3. MİNİMALİST GRİ — çok boşluklu, ince çizgiler, büyük harf başlıklar
# --------------------------------------------------------------------------

def draw_minimalist_gray(c, data):
    accent = HexColor("#9a9a9a")
    text_color = HexColor("#3a3a3a")
    muted = HexColor("#8c8c8c")
    dark = HexColor("#202020")
    margin = 60
    max_w = PAGE_W - 2 * margin
    y = PAGE_H - 70

    c.setFont(FONT_REGULAR, 22)
    c.setFillColor(dark)
    name = _g(data, "full_name").upper()
    c.drawString(margin, y, name)
    y -= 18
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 10.5)
        c.setFillColor(accent)
        c.drawString(margin, y, data["job_title"].upper())
        y -= 14

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_REGULAR, 8.6, muted, separator="    ", leading=12)
        y -= 2

    draw_hline(c, margin, PAGE_W - margin, y, HexColor("#dddddd"), 0.6)
    y -= 24

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_REGULAR, 10.5)
        c.setFillColor(accent)
        # harfler arası boşluklu görünüm
        spaced = "  ".join(list(title.upper()))
        c.drawString(margin, y, spaced)
        return y - 15

    _sections_generic(c, flow, data, margin, max_w, y, heading,
                       body_font=FONT_REGULAR, body_size=9.6, text_color=text_color,
                       bold_font=FONT_BOLD, muted=muted, bullet_color=accent,
                       leading=14)


# --------------------------------------------------------------------------
# 4. İKİ SÜTUN KOYU KENAR — sol koyu kenar çubuğu (sidebar)
# --------------------------------------------------------------------------

def draw_dark_sidebar(c, data):
    side_w = 190
    side_color = HexColor("#1f2733")
    side_accent = HexColor("#4fb0ae")
    text_color = HexColor("#2b2b2b")
    muted = HexColor("#6b6b6b")

    def draw_sidebar_bg(cc):
        cc.setFillColor(side_color)
        cc.rect(0, 0, side_w, PAGE_H, stroke=0, fill=1)

    draw_sidebar_bg(c)

    # Avatar dairesi (baş harfler)
    cx, cy_, r = side_w / 2, PAGE_H - 90, 34
    c.setFillColor(side_accent)
    c.circle(cx, cy_, r, stroke=0, fill=1)
    c.setFont(FONT_BOLD, 22)
    c.setFillColor(side_color)
    c.drawCentredString(cx, cy_ - 8, initials(_g(data, "full_name", "AS")))

    sy = PAGE_H - 150
    c.setFont(FONT_BOLD, 15)
    c.setFillColor(white)
    for line in wrap_text(_g(data, "full_name"), FONT_BOLD, 15, side_w - 30):
        c.drawCentredString(cx, sy, line)
        sy -= 17
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 9.5)
        c.setFillColor(side_accent)
        for line in wrap_text(data["job_title"], FONT_REGULAR, 9.5, side_w - 30):
            c.drawCentredString(cx, sy, line)
            sy -= 12
    sy -= 14

    sflow = PageFlow(c, on_new_page=lambda cc, pi: (15, PAGE_H - 60, side_w - 30))

    def side_heading(title, y):
        y = sflow.ensure_space(y, 18)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(side_accent)
        c.drawString(15, y, title.upper())
        y -= 4
        draw_hline(c, 15, side_w - 15, y, HexColor("#3a4552"), 0.6)
        return y - 12

    sy = side_heading(_t(data, "contact"), sy)
    for label, url in contact_items(data):
        sy = sflow.ensure_space(sy, 12)
        c.setFont(FONT_REGULAR, 8.3)
        c.setFillColor(HexColor("#c8d0da"))
        for line in wrap_text(label, FONT_REGULAR, 8.3, side_w - 30):
            sy = sflow.ensure_space(sy, 11)
            c.drawString(15, sy, line)
            if url:
                w = c.stringWidth(line, FONT_REGULAR, 8.3)
                c.linkURL(url, (15, sy - 1, 15 + w, sy + 9), relative=0)
                c.setStrokeColor(HexColor("#c8d0da"))
                c.setLineWidth(0.5)
                c.line(15, sy - 1, 15 + w, sy - 1)
            sy -= 11
    sy -= 8

    if data.get("skills"):
        sy = side_heading(_t(data, "skills"), sy)
        for sk in data["skills"]:
            sy = sflow.ensure_space(sy, 11)
            draw_bullet_dot(c, 18, sy + 3, side_accent)
            c.setFont(FONT_REGULAR, 8.4)
            c.setFillColor(HexColor("#dfe5eb"))
            c.drawString(24, sy, sk)
            sy -= 12
        sy -= 8

    if data.get("languages"):
        sy = side_heading(_t(data, "languages"), sy)
        for lg in data["languages"]:
            sy = sflow.ensure_space(sy, 11)
            draw_bullet_dot(c, 18, sy + 3, side_accent)
            c.setFont(FONT_REGULAR, 8.4)
            c.setFillColor(HexColor("#dfe5eb"))
            c.drawString(24, sy, lg)
            sy -= 12
        sy -= 8

    if data.get("certifications"):
        sy = side_heading(_t(data, "certifications"), sy)
        for ce in data["certifications"]:
            sy = sflow.ensure_space(sy, 11)
            for line in wrap_text(ce, FONT_REGULAR, 8.2, side_w - 34):
                sy = sflow.ensure_space(sy, 11)
                c.setFont(FONT_REGULAR, 8.2)
                c.setFillColor(HexColor("#dfe5eb"))
                c.drawString(24, sy, line)
                sy -= 11
            sy -= 3

    # --- sağ ana içerik ---
    right_margin = side_w + 30
    max_w = PAGE_W - right_margin - 40
    y = PAGE_H - 60

    def right_new_page(cc, pi):
        draw_sidebar_bg(cc)
        return right_margin, PAGE_H - 55, max_w

    flow = PageFlow(c, on_new_page=right_new_page)

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_BOLD, 13)
        c.setFillColor(side_color)
        c.drawString(right_margin, y, title)
        y -= 5
        draw_hline(c, right_margin, right_margin + max_w, y, side_accent, 1.4)
        return y - 14

    lang = _lang(data)

    if data.get("summary"):
        y = heading(_t(data, "summary"), y)
        y, _, _ = flow.draw_paragraph(data["summary"], right_margin, y, max_w,
                                       FONT_REGULAR, 9.8, 13.6, text_color)
        y -= 8

    if data.get("experience"):
        y = heading(_t(data, "experience"), y)
        for exp in data["experience"]:
            y = flow.ensure_space(y, 24)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(FONT_BOLD, 10.3)
            c.setFillColor(text_color)
            c.drawString(right_margin, y, _c or _p)
            dr = date_range(exp, lang)
            if dr:
                c.setFont(FONT_REGULAR, 8.5)
                c.setFillColor(muted)
                c.drawRightString(right_margin + max_w, y, dr)
            y -= 12.5
            if _c and _p:
                c.setFont(FONT_ITALIC, 9.3)
                c.setFillColor(side_accent)
                c.drawString(right_margin, y, _p)
                y -= 12.5
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, 13.6)
                    draw_bullet_dot(c, right_margin + 3, y + 3, side_accent)
                    y, _, _ = flow.draw_paragraph(line.strip(), right_margin + 10, y,
                                                   max_w - 10, FONT_REGULAR, 9.4, 13.6, text_color)
            y -= 8

    if data.get("education"):
        y = heading(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(FONT_BOLD, 10.3)
            c.setFillColor(text_color)
            c.drawString(right_margin, y, edu.get("degree", ""))
            dr = date_range(edu, lang)
            if dr:
                c.setFont(FONT_REGULAR, 8.5)
                c.setFillColor(muted)
                c.drawRightString(right_margin + max_w, y, dr)
            y -= 12.5
            if edu.get("school"):
                c.setFont(FONT_ITALIC, 9.3)
                c.setFillColor(side_accent)
                c.drawString(right_margin, y, edu["school"])
                y -= 12.5
            if edu.get("description"):
                y, _, _ = flow.draw_paragraph(edu["description"], right_margin, y, max_w,
                                               FONT_REGULAR, 9.4, 13.6, text_color)
            y -= 8


# --------------------------------------------------------------------------
# 5. ZAMAN ÇİZELGESİ — deneyimler dikey timeline üzerinde
# --------------------------------------------------------------------------

def draw_timeline(c, data):
    accent = HexColor("#c1440e")
    line_color = HexColor("#e8c3b0")
    text_color = HexColor("#2b2b2b")
    muted = HexColor("#6b6b6b")
    margin = 55
    max_w = PAGE_W - 2 * margin
    y = PAGE_H - 65

    c.setFont(FONT_BOLD, 24)
    c.setFillColor(HexColor("#1c1c1c"))
    c.drawString(margin, y, _g(data, "full_name"))
    y -= 20
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 12.5)
        c.setFillColor(accent)
        c.drawString(margin, y, data["job_title"])
        y -= 16

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_REGULAR, 8.8, muted, separator="   |   ", leading=12)
        y -= 2

    draw_hline(c, margin, PAGE_W - margin, y, accent, 1.4)
    y -= 22

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_BOLD, 12.5)
        c.setFillColor(accent)
        c.drawString(margin, y, title)
        return y - 16

    lang = _lang(data)

    if data.get("summary"):
        y = heading(_t(data, "summary"), y)
        y, _, _ = flow.draw_paragraph(data["summary"], margin, y, max_w,
                                       FONT_REGULAR, 9.8, 13.6, text_color)
        y -= 10

    if data.get("experience"):
        y = heading(_t(data, "experience"), y)
        tx = margin + 6
        for i, exp in enumerate(data["experience"]):
            y = flow.ensure_space(y, 30)
            top_y = y
            draw_bullet_dot(c, tx, y + 2, accent, r=3.6)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(FONT_BOLD, 10.4)
            c.setFillColor(text_color)
            c.drawString(tx + 14, y, _c or _p)
            dr = date_range(exp, lang)
            if dr:
                c.setFont(FONT_ITALIC, 8.6)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if _c and _p:
                c.setFont(FONT_REGULAR, 9.2)
                c.setFillColor(accent)
                c.drawString(tx + 14, y, _p)
                y -= 12.5
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, 13.2)
                    y, _, _ = flow.draw_paragraph("– " + line.strip(), tx + 14, y,
                                                   max_w - 14, FONT_REGULAR, 9.2, 13.2, text_color)
            bottom_y = y - 4
            if i < len(data["experience"]) - 1:
                c.setStrokeColor(line_color)
                c.setLineWidth(1.6)
                c.line(tx, top_y - 2, tx, bottom_y)
            y = bottom_y - 8

    if data.get("education"):
        y = heading(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(FONT_BOLD, 10.2)
            c.setFillColor(text_color)
            c.drawString(margin, y, edu.get("degree", ""))
            dr = date_range(edu, lang)
            if dr:
                c.setFont(FONT_ITALIC, 8.6)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if edu.get("school"):
                c.setFont(FONT_REGULAR, 9.2)
                c.setFillColor(accent)
                c.drawString(margin, y, edu["school"])
                y -= 12.5
            y -= 6

    if data.get("skills"):
        y = heading(_t(data, "skills"), y)
        y = _draw_tag_row(c, flow, data["skills"], margin, y, max_w, accent)
        y -= 8

    if data.get("languages"):
        y = heading(_t(data, "languages"), y)
        y, _, _ = flow.draw_paragraph("  •  ".join(data["languages"]), margin, y, max_w,
                                       FONT_REGULAR, 9.6, 13.6, text_color)


def _draw_tag_row(c, flow, items, x0, y, max_w, accent, font=FONT_REGULAR, size=8.6,
                   pad_x=8, pad_y=4, gap=6, row_h=18):
    x = x0
    for item in items:
        w = c.stringWidth(item, font, size) + 2 * pad_x
        if x + w > x0 + max_w:
            x = x0
            y = flow.ensure_space(y, row_h + gap) - row_h
        else:
            y = flow.ensure_space(y, row_h)
        draw_rounded_box(c, x, y - 4, w, row_h, 8, HexColor("#fbe7dd"))
        c.setFont(font, size)
        c.setFillColor(accent)
        c.drawString(x + pad_x, y, item)
        x += w + gap
    return y - row_h - 2


# --------------------------------------------------------------------------
# 6. YARATICI RENKLİ — renkli başlık kutusu, pastel rozet etiketler
# --------------------------------------------------------------------------

def draw_creative(c, data):
    accent = HexColor("#7b2ff7")
    accent2 = HexColor("#f72585")
    text_color = HexColor("#2b2b2b")
    muted = HexColor("#6b6b6b")
    margin = 50
    max_w = PAGE_W - 2 * margin

    citems = contact_items(data)
    labels = [label for label, _ in citems]
    contact_lines_est = len(wrap_text("   •   ".join(labels), FONT_REGULAR, 8.6,
                                      max_w - 26)) if labels else 0
    box_h = 78 + contact_lines_est * 11
    draw_rounded_box(c, margin, PAGE_H - box_h - 30, PAGE_W - 2 * margin, box_h, 14, accent)
    c.setFillColor(accent2)
    c.roundRect(margin, PAGE_H - box_h - 30, 10, box_h, 5, stroke=0, fill=1)

    c.setFont(FONT_BOLD, 22)
    c.setFillColor(white)
    c.drawString(margin + 26, PAGE_H - 58, _g(data, "full_name"))
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 12)
        c.setFillColor(HexColor("#f0e2ff"))
        c.drawString(margin + 26, PAGE_H - 76, data["job_title"])

    if citems:
        draw_contact_line(c, data, margin + 26, PAGE_H - 96,
                          max_w - 26, FONT_REGULAR, 8.6, HexColor("#f0e2ff"),
                          separator="   •   ", leading=11)

    y = PAGE_H - box_h - 55

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 24)
        w = c.stringWidth(title, FONT_BOLD, 11) + 20
        draw_rounded_box(c, margin, y - 4, w, 18, 9, accent2)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(white)
        c.drawString(margin + 10, y, title)
        return y - 18

    lang = _lang(data)

    if data.get("summary"):
        y = heading(_t(data, "summary"), y)
        y, _, _ = flow.draw_paragraph(data["summary"], margin, y, max_w,
                                       FONT_REGULAR, 9.8, 13.6, text_color)
        y -= 10

    if data.get("experience"):
        y = heading(_t(data, "experience"), y)
        for exp in data["experience"]:
            y = flow.ensure_space(y, 26)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(FONT_BOLD, 10.4)
            c.setFillColor(accent)
            c.drawString(margin, y, _c or _p)
            dr = date_range(exp, lang)
            if dr:
                c.setFont(FONT_REGULAR, 8.6)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if _c and _p:
                c.setFont(FONT_ITALIC, 9.3)
                c.setFillColor(text_color)
                c.drawString(margin, y, _p)
                y -= 12.5
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, 13.4)
                    draw_bullet_dot(c, margin + 3, y + 3, accent2)
                    y, _, _ = flow.draw_paragraph(line.strip(), margin + 10, y,
                                                   max_w - 10, FONT_REGULAR, 9.3, 13.4, text_color)
            y -= 8

    if data.get("education"):
        y = heading(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(FONT_BOLD, 10.4)
            c.setFillColor(accent)
            c.drawString(margin, y, edu.get("degree", ""))
            dr = date_range(edu, lang)
            if dr:
                c.setFont(FONT_REGULAR, 8.6)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if edu.get("school"):
                c.setFont(FONT_ITALIC, 9.3)
                c.setFillColor(text_color)
                c.drawString(margin, y, edu["school"])
                y -= 12.5
            y -= 6

    if data.get("skills"):
        y = heading(_t(data, "skills"), y)
        y = _draw_tag_row(c, flow, data["skills"], margin, y, max_w, accent)
        y -= 6

    if data.get("languages"):
        y = heading(_t(data, "languages"), y)
        y = _draw_tag_row(c, flow, data["languages"], margin, y, max_w, accent2)


# --------------------------------------------------------------------------
# 7. KURUMSAL YEŞİL — klasik yapı + tam boy sol şerit
# --------------------------------------------------------------------------

def draw_corporate_green(c, data):
    accent = HexColor("#1f7a4d")
    dark = HexColor("#123c26")
    text_color = HexColor("#26312b")
    muted = HexColor("#66756d")
    strip_w = 8
    margin = 55
    max_w = PAGE_W - 2 * margin - strip_w

    def draw_strip(cc):
        cc.setFillColor(accent)
        cc.rect(0, 0, strip_w, PAGE_H, stroke=0, fill=1)

    draw_strip(c)
    y = PAGE_H - 65

    c.setFont(FONT_BOLD, 23)
    c.setFillColor(dark)
    c.drawString(margin, y, _g(data, "full_name"))
    y -= 20
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 12)
        c.setFillColor(accent)
        c.drawString(margin, y, data["job_title"])
        y -= 16

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_REGULAR, 8.8, muted, separator="   |   ", leading=12)
        y -= 2

    draw_hline(c, margin, PAGE_W - margin, y, HexColor("#cfe3d7"), 1)
    y -= 22

    def new_page(cc, pi):
        draw_strip(cc)
        return margin, PAGE_H - 55, max_w

    flow = PageFlow(c, on_new_page=new_page)

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_BOLD, 12.3)
        c.setFillColor(accent)
        c.drawString(margin, y, title)
        y -= 5
        draw_hline(c, margin, PAGE_W - margin, y, HexColor("#dcece2"), 0.7)
        return y - 14

    _sections_generic(c, flow, data, margin, max_w, y, heading,
                       body_font=FONT_REGULAR, body_size=9.8, text_color=text_color,
                       bold_font=FONT_BOLD, muted=muted, bullet_color=accent)


# --------------------------------------------------------------------------
# 8. ZARİF BORDO — serif font, ortalanmış, ince çift çizgi
# --------------------------------------------------------------------------

def draw_elegant_maroon(c, data):
    accent = HexColor("#7a1f2b")
    text_color = HexColor("#2c2622")
    muted = HexColor("#8a7a75")
    margin = 60
    max_w = PAGE_W - 2 * margin
    y = PAGE_H - 70

    c.setFont(FONT_SERIF_BOLD, 25)
    c.setFillColor(accent)
    c.drawCentredString(PAGE_W / 2, y, _g(data, "full_name"))
    y -= 20
    if data.get("job_title"):
        c.setFont(FONT_SERIF, 12)
        c.setFillColor(HexColor("#5a4f49"))
        c.drawCentredString(PAGE_W / 2, y, data["job_title"])
        y -= 16

    draw_hline(c, PAGE_W / 2 - 90, PAGE_W / 2 - 10, y, accent, 0.8)
    draw_bullet_dot(c, PAGE_W / 2, y + 2, accent, r=1.6)
    draw_hline(c, PAGE_W / 2 + 10, PAGE_W / 2 + 90, y, accent, 0.8)
    y -= 16

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_SERIF, 8.8, muted, separator="   ·   ",
                              align="center", leading=12)
        y -= 10

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 22)
        c.setFont(FONT_SERIF_BOLD, 12.5)
        c.setFillColor(accent)
        c.drawCentredString(PAGE_W / 2, y, title)
        y -= 4
        draw_hline(c, PAGE_W / 2 - 60, PAGE_W / 2 + 60, y, HexColor("#e3d3d3"), 0.6)
        return y - 15

    def para(text, y):
        y, _, _ = flow.draw_paragraph(text, margin, y, max_w, FONT_SERIF, 9.7, 14, text_color)
        return y

    lang = _lang(data)

    if data.get("summary"):
        y = heading(_t(data, "summary"), y)
        y = para(data["summary"], y)
        y -= 8

    if data.get("experience"):
        y = heading(_t(data, "experience"), y)
        for exp in data["experience"]:
            y = flow.ensure_space(y, 26)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(FONT_SERIF_BOLD, 10.4)
            c.setFillColor(text_color)
            c.drawCentredString(PAGE_W / 2, y, _c or _p)
            y -= 12.5
            sub = _p if _c else ""
            dr = date_range(exp, lang)
            if sub or dr:
                c.setFont(FONT_SERIF, 8.8)
                c.setFillColor(muted)
                c.drawCentredString(PAGE_W / 2, y, f"{sub}   ({dr})" if dr else sub)
                y -= 13
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, 14)
                    c.setFont(FONT_SERIF, 9.3)
                    c.setFillColor(text_color)
                    for wline in wrap_text(line.strip(), FONT_SERIF, 9.3, max_w):
                        y = flow.ensure_space(y, 14)
                        c.drawCentredString(PAGE_W / 2, y, wline)
                        y -= 14
            y -= 10

    if data.get("education"):
        y = heading(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(FONT_SERIF_BOLD, 10.4)
            c.setFillColor(text_color)
            c.drawCentredString(PAGE_W / 2, y, edu.get("degree", ""))
            y -= 12.5
            sub = edu.get("school", "")
            dr = date_range(edu, lang)
            if sub or dr:
                c.setFont(FONT_SERIF, 8.8)
                c.setFillColor(muted)
                c.drawCentredString(PAGE_W / 2, y, f"{sub}   ({dr})" if dr else sub)
                y -= 13
            y -= 8

    if data.get("skills"):
        y = heading(_t(data, "skills"), y)
        y, _, _ = flow.draw_paragraph("  ·  ".join(data["skills"]), margin, y, max_w,
                                       FONT_SERIF, 9.5, 14, text_color, align="center")
        y -= 8

    if data.get("languages"):
        y = heading(_t(data, "languages"), y)
        c.setFont(FONT_SERIF, 9.5)
        c.setFillColor(text_color)
        c.drawCentredString(PAGE_W / 2, y, "  ·  ".join(data["languages"]))


# --------------------------------------------------------------------------
# 9. TEKNOLOJİ KOYU TEMA — tam koyu arka plan, neon vurgu, mono font başlıklar
# --------------------------------------------------------------------------

def draw_tech_dark(c, data):
    bg = HexColor("#0d1117")
    accent = HexColor("#39d9c4")
    accent2 = HexColor("#ff6b6b")
    text_color = HexColor("#c9d1d9")
    muted = HexColor("#8b949e")
    margin = 55
    max_w = PAGE_W - 2 * margin

    def draw_bg(cc):
        cc.setFillColor(bg)
        cc.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    draw_bg(c)
    y = PAGE_H - 65

    c.setFont(FONT_MONO_BOLD, 20)
    c.setFillColor(accent)
    c.drawString(margin, y, "> " + _g(data, "full_name"))
    y -= 20
    if data.get("job_title"):
        c.setFont(FONT_MONO, 10.5)
        c.setFillColor(text_color)
        c.drawString(margin, y, "# " + data["job_title"])
        y -= 15

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_MONO, 8.3, muted, separator=" | ", leading=11)
        y -= 4

    draw_hline(c, margin, PAGE_W - margin, y, HexColor("#21262d"), 1)
    y -= 20

    flow = PageFlow(c, on_new_page=lambda cc, pi: (draw_bg(cc), (margin, PAGE_H - 55, max_w))[1])

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFont(FONT_MONO_BOLD, 11.5)
        c.setFillColor(accent2)
        c.drawString(margin, y, "## " + title)
        return y - 16

    lang = _lang(data)

    if data.get("summary"):
        y = heading(_t(data, "summary"), y)
        y, _, _ = flow.draw_paragraph(data["summary"], margin, y, max_w,
                                       FONT_REGULAR, 9.6, 13.6, text_color)
        y -= 8

    if data.get("experience"):
        y = heading(_t(data, "experience"), y)
        for exp in data["experience"]:
            y = flow.ensure_space(y, 26)
            _c = exp.get("company", "")
            _p = exp.get("position", "")
            c.setFont(FONT_MONO_BOLD, 10)
            c.setFillColor(accent)
            c.drawString(margin, y, _c or _p)
            dr = date_range(exp, lang)
            if dr:
                c.setFont(FONT_MONO, 8.2)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if _c and _p:
                c.setFont(FONT_ITALIC, 9.2)
                c.setFillColor(text_color)
                c.drawString(margin, y, _p)
                y -= 12.5
            if exp.get("description"):
                for line in str(exp["description"]).split("\n"):
                    if not line.strip():
                        continue
                    y = flow.ensure_space(y, 13.4)
                    c.setFont(FONT_MONO, 8.6)
                    c.setFillColor(muted)
                    c.drawString(margin, y, "$")
                    y, _, _ = flow.draw_paragraph(line.strip(), margin + 12, y,
                                                   max_w - 12, FONT_REGULAR, 9.1, 13.4, text_color)
            y -= 8

    if data.get("education"):
        y = heading(_t(data, "education"), y)
        for edu in data["education"]:
            y = flow.ensure_space(y, 24)
            c.setFont(FONT_MONO_BOLD, 10)
            c.setFillColor(accent)
            c.drawString(margin, y, edu.get("degree", ""))
            dr = date_range(edu, lang)
            if dr:
                c.setFont(FONT_MONO, 8.2)
                c.setFillColor(muted)
                c.drawRightString(margin + max_w, y, dr)
            y -= 12.5
            if edu.get("school"):
                c.setFont(FONT_ITALIC, 9.2)
                c.setFillColor(text_color)
                c.drawString(margin, y, edu["school"])
                y -= 12.5
            y -= 6

    if data.get("skills"):
        y = heading(_t(data, "skills"), y)
        y = _draw_tag_row(c, flow, data["skills"], margin, y, max_w, accent)
        y -= 6

    if data.get("languages"):
        y = heading(_t(data, "languages"), y)
        y, _, _ = flow.draw_paragraph("  •  ".join(data["languages"]), margin, y, max_w,
                                       FONT_REGULAR, 9.4, 13.4, text_color)


# --------------------------------------------------------------------------
# 10. SADE TURUNCU — beyaz zemin, turuncu vurgular, kompakt tek sütun
# --------------------------------------------------------------------------

def draw_simple_orange(c, data):
    accent = HexColor("#e8590c")
    text_color = HexColor("#2b2b2b")
    muted = HexColor("#6b6b6b")
    margin = 55
    max_w = PAGE_W - 2 * margin
    y = PAGE_H - 62

    c.setFillColor(accent)
    c.rect(margin, y - 4, 34, 4, stroke=0, fill=1)
    y -= 18
    c.setFont(FONT_BOLD, 22)
    c.setFillColor(HexColor("#1c1c1c"))
    c.drawString(margin, y, _g(data, "full_name"))
    y -= 18
    if data.get("job_title"):
        c.setFont(FONT_REGULAR, 12)
        c.setFillColor(accent)
        c.drawString(margin, y, data["job_title"])
        y -= 15

    if contact_items(data):
        y = draw_contact_line(c, data, margin, y, max_w,
                              FONT_REGULAR, 8.8, muted, separator="   •   ", leading=12)
        y -= 6

    flow = PageFlow(c, on_new_page=lambda cc, pi: _plain_new_page(cc, margin))

    def heading(title, y):
        y = flow.ensure_space(y, 20)
        c.setFillColor(accent)
        c.rect(margin, y - 2, 3, 12, stroke=0, fill=1)
        c.setFont(FONT_BOLD, 11.8)
        c.setFillColor(HexColor("#1c1c1c"))
        c.drawString(margin + 9, y, title)
        return y - 16

    _sections_generic(c, flow, data, margin, max_w, y, heading,
                       body_font=FONT_REGULAR, body_size=9.7, text_color=text_color,
                       bold_font=FONT_BOLD, muted=muted, bullet_color=accent)


# --------------------------------------------------------------------------
# Şablon kayıt defteri
# --------------------------------------------------------------------------

TEMPLATES = [
    {"id": "classic", "name": "1. Klasik", "func": draw_classic,
     "desc": "Sade siyah-beyaz, ortalanmış başlık"},
    {"id": "modern_blue", "name": "2. Modern Mavi", "func": draw_modern_blue,
     "desc": "Üstte koyu mavi başlık bandı"},
    {"id": "minimalist_gray", "name": "3. Minimalist Gri", "func": draw_minimalist_gray,
     "desc": "Bol boşluklu, ince çizgili, büyük harf başlıklar"},
    {"id": "dark_sidebar", "name": "4. İki Sütun Koyu Kenar", "func": draw_dark_sidebar,
     "desc": "Sol koyu kenar çubuğunda iletişim/yetenekler"},
    {"id": "timeline", "name": "5. Zaman Çizelgesi", "func": draw_timeline,
     "desc": "Deneyimler dikey zaman çizelgesinde"},
    {"id": "creative", "name": "6. Yaratıcı Renkli", "func": draw_creative,
     "desc": "Mor-pembe renkli başlık kutusu ve rozet etiketler"},
    {"id": "corporate_green", "name": "7. Kurumsal Yeşil", "func": draw_corporate_green,
     "desc": "Yeşil vurgulu, kurumsal ve düzenli"},
    {"id": "elegant_maroon", "name": "8. Zarif Bordo", "func": draw_elegant_maroon,
     "desc": "Serif font, ortalanmış zarif tasarım"},
    {"id": "tech_dark", "name": "9. Teknoloji Koyu Tema", "func": draw_tech_dark,
     "desc": "Koyu arka plan, neon vurgu, mono font"},
    {"id": "simple_orange", "name": "10. Sade Turuncu", "func": draw_simple_orange,
     "desc": "Beyaz zemin, turuncu vurgulu kompakt tasarım"},
]

TEMPLATES_BY_ID = {t["id"]: t for t in TEMPLATES}


def generate_cv_pdf(template_id, data, output_path):
    """Verilen şablon id'siyle CV PDF'ini output_path konumuna üretir."""
    from reportlab.pdfgen import canvas as rl_canvas
    if template_id not in TEMPLATES_BY_ID:
        raise ValueError(f"Bilinmeyen şablon: {template_id}")
    c = rl_canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(_g(data, "full_name", "CV"))
    TEMPLATES_BY_ID[template_id]["func"](c, data)
    c.showPage()
    c.save()
    return output_path