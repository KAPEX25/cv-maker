# -*- coding: utf-8 -*-
"""
build_icon.py — uygulama ikonlarını üretir.

- logos/logo.png varsa  : ondan çoklu boyutlu app.ico + app.icns üretir.
- logos/logo.png yoksa  : özel logon (git'e push edilmeyen) yok demektir;
                          otomatik bir "CV" yer tutucusu (placeholder) üretir.
                          Böylece public repo'da GitHub Actions derlemesi de
                          logosuz çalışır.

Çalıştırmak (proje klasörüne):
    python build_icon.py
"""
import io
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

# Windows'ta konsol utf-8 olmayabilir (cp1252) — Türkçe çıktılar patlamasın.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

SRC = os.path.join("logos", "logo.png")
DST_ICO = os.path.join("logos", "app.ico")
DST_ICNS = os.path.join("logos", "app.icns")

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def make_placeholder(size=1024):
    """Logosuz derlemeler için basit 'CV' rozeti üretir."""
    img = Image.new("RGBA", (size, size), (37, 78, 152, 255))
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=255)
    img.putalpha(mask)

    d = ImageDraw.Draw(img)
    font = None
    for path in ("fonts/DejaVuSans-Bold.ttf", os.path.join("fonts", "DejaVuSans-Bold.ttf")):
        if os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, size // 3)
                break
            except Exception:
                font = None
    if font is None:
        font = ImageFont.load_default()

    txt = d.textbbox((0, 0), "CV", font=font)
    w, h = txt[2] - txt[0], txt[3] - txt[1]
    d.text(
        ((size - w) // 2 - txt[0], (size - h) // 2 - txt[1]),
        "CV", fill=(255, 255, 255, 255), font=font,
    )
    return img


def build_ico(img, sizes):
    """Çoklu boyutlu, PNG kodlu çerçeveler içeren bir .ico dosyası üretir."""
    frames = []
    for s in sizes:
        resized = img.resize((s, s), Image.LANCZOS) if (img.width, img.height) != (s, s) else img
        buf = io.BytesIO()
        resized.save(buf, format="PNG")
        frames.append((buf.getvalue(), s))

    header = struct.pack("<HHH", 0, 1, len(frames))
    offset = 6 + 16 * len(frames)

    entries = b""
    png_data = b""
    for data, s in frames:
        w = 0 if s >= 256 else s  # ICO'da 256 = 0
        entries += struct.pack(
            "<BBBBHHII", w, w, 0, 0, 1, 32, len(data), offset
        )
        png_data += data
        offset += len(data)

    return header + entries + png_data


def build_icns(img, sizes):
    """Çoklu boyutlu, PNG kodlu bir .icns dosyası üretir."""
    TYPES = {16: b"icp4", 32: b"icp5", 64: b"icp6", 128: b"ic07",
             256: b"ic08", 512: b"ic09", 1024: b"ic10"}
    data = b""
    total = 0
    for s in sizes:
        resized = img.resize((s, s), Image.LANCZOS) if (img.width, img.height) != (s, s) else img
        buf = io.BytesIO()
        resized.save(buf, format="PNG")
        png = buf.getvalue()
        chunk = TYPES[s] + struct.pack(">I", len(png) + 8) + png
        data += chunk
        total += len(chunk)

    return b"icns" + struct.pack(">I", total + 8) + data


def main():
    os.makedirs("logos", exist_ok=True)

    if os.path.isfile(SRC):
        img = Image.open(SRC).convert("RGBA")
        print(f"Kullanılıyor: {SRC}")
    else:
        print("logos/logo.png bulunamadı — otomatik placeholder ikonu üretiliyor.")
        img = make_placeholder()
        img.save(SRC)

    with open(DST_ICO, "wb") as f:
        f.write(build_ico(img, ICO_SIZES))
    with open(DST_ICNS, "wb") as f:
        f.write(build_icns(img, ICNS_SIZES))

    print(f"Üretildi: {DST_ICO} ({ICO_SIZES}) + {DST_ICNS} ({ICNS_SIZES})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())