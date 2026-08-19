#!/bin/bash
# build_mac.sh — macOS üzerinde CV-Olusturucu.app ve .dmg üretir.
#
# Kullanım:
#   chmod +x build_mac.sh
#   ./build_mac.sh
#
# Ön koşullar (macOS üzerinde):
#   brew install python-tk
#   pip install pyinstaller reportlab pillow
set -euo pipefail
cd "$(dirname "$0")"

# Eski Intel Mac'lerde de çalışsın: minimum macOS sürümünü düşür.
# (Eski değerin üstüne çıkmaz; PyInstaller/Python'un alt limitlerine takılır.)
export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-10.13}"
export PYTHONIOENCODING=utf-8

echo "==> 1/3: .app paketi derleniyor (pyinstaller)... [min macOS: $MACOSX_DEPLOYMENT_TARGET]"
pyinstaller CV-Olusturucu-mac.spec --noconfirm

APP="dist/CV-Olusturucu.app"
if [ ! -d "$APP" ]; then
    echo "Hata: $APP oluşturulamadı!" >&2
    exit 1
fi

echo "==> 2/3: .dmg oluşturuluyor..."
DMG="dist/CV-Olusturucu.dmg"
rm -f "$DMG"

# .app'i dmg içine yerleştirir (sürükle-bırak /Applications kısayolu ile)
STAGE="build/dmg_stage"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

hdiutil create -volname "CV Oluşturucu" \
    -srcfolder "$STAGE" \
    -ov -format UDZO "$DMG"

echo "==> 3/3: Kod imzalama (isteğe bağlı, Apple Geliştirici hesabı gerekir)"
if [ -n "${CODESIGN_IDENTITY:-}" ]; then
    codesign --force --deep --sign "$CODESIGN_IDENTITY" "$APP"
    echo "   İmzalandı: $APP"
else
    echo "   Atlanıyor (CODESIGN_IDENTITY tanımlanmadı)."
fi

echo ""
echo "TAMAM! Çıktılar:"
echo "  .app: $APP"
echo "  .dmg: $DMG"