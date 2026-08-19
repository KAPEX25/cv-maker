#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_universal.py — iki PyInstaller macOS app'ini (arm64 + x86_64) birleştirip
Universal2 (.app) ve .dmg üretir. Sadece macOS üzerinde çalışır (lipo/hdiutil).

Kullanım:
    python build_universal.py <arm.app> <intel.app> <cikti.app> [cikti.dmg]
"""
import os
import shutil
import subprocess
import sys


def is_macho(path):
    """Dosya Mach-O ise True döner."""
    try:
        out = subprocess.run(["file", "-b", path], capture_output=True, text=True).stdout
        return "Mach-O" in out
    except Exception:
        return False


def walk_files(base):
    for dp, _dn, fns in os.walk(base):
        for f in fns:
            yield os.path.join(dp, f)


def main():
    if len(sys.argv) < 4:
        print("Usage: build_universal.py <arm.app> <intel.app> <out.app> [out.dmg]")
        return 1

    arm, intel, out = sys.argv[1], sys.argv[2], sys.argv[3]
    dmg = sys.argv[4] if len(sys.argv) > 4 else None

    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(arm, out)  # arm64 app'ini taban olarak kopyala

    arm_contents = os.path.join(arm, "Contents")
    intel_contents = os.path.join(intel, "Contents")
    out_contents = os.path.join(out, "Contents")

    merged = 0
    for p_arm in walk_files(arm):
        if os.path.islink(p_arm):
            continue
        rel = os.path.relpath(p_arm, arm_contents)
        p_intel = os.path.join(intel_contents, rel)
        p_out = os.path.join(out_contents, rel)
        if os.path.exists(p_intel) and is_macho(p_arm):
            # iki işlemci dilimini lipo ile tek dosyada birleştir (universal2)
            subprocess.run(
                ["lipo", "-create", "-output", p_out, p_arm, p_intel], check=True
            )
            merged += 1

    print(f"lipo ile {merged} Mach-O dosyası birleştirildi.")

    # doğrulama: ana yürütülebilir hem arm64 hem x86_64 içermeli
    exe = os.path.join(out, "Contents", "MacOS", "CV-Olusturucu")
    if os.path.exists(exe):
        subprocess.run(["lipo", "-info", exe], check=True)

    # ad-hoc imza (Gatesiz/dağıtımsız çalıştırma için macOS'un istediği imza)
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", out], check=True)

    if dmg:
        stage = os.path.join(os.path.dirname(dmg) or ".", "_stage")
        if os.path.exists(stage):
            shutil.rmtree(stage)
        os.makedirs(stage)
        shutil.copytree(out, os.path.join(stage, "CV-Olusturucu.app"))
        os.symlink("/Applications", os.path.join(stage, "Applications"))
        subprocess.run(
            ["hdiutil", "create", "-volname", "CV Oluşturucu",
             "-srcfolder", stage, "-ov", "-format", "UDZO", dmg],
            check=True,
        )
        print(f"DMG oluşturuldu: {dmg}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())