# -*- coding: utf-8 -*-
"""
app.py — CV Oluşturucu
Bilgilerini doldurup 10 farklı şablondan birini seçerek PDF CV üreten
Tkinter masaüstü uygulaması.

Çalıştırmak için:
    python app.py

Gereksinimler: reportlab (pip install reportlab). Tkinter genelde Python
ile birlikte gelir; gelmediyse README.md içindeki kurulum notuna bakın.
"""

import os
import sys
import json
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from templates import TEMPLATES, generate_cv_pdf


APP_TITLE = "CV Oluşturucu — 10 Şablon / CV Builder — 10 Templates"

# --------------------------------------------------------------------------
# Kaynak dosya yolu (hem normal çalıştırmada hem PyInstaller exe'sinde çalışır)
# --------------------------------------------------------------------------
def resource_path(relative):
    """PyInstaller ile derlenmiş exe'de _MEIPASS'tan, aksi halde dosya
    klasöründen kaynak arar."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def set_app_icon(root):
    """Pencerenin / görev çubuğunun ikonunu logos/ klasöründen ayarlar.

    Önce .ico (Windows iconbitmap), yoksa PNG/gif/jpg (iconphoto) kullanır.
    Dosya yoksa sessizce geçilir — uygulama yine de açılır.
    """
    logo_dir = resource_path("logos")
    if not os.path.isdir(logo_dir):
        return
    names = sorted(os.listdir(logo_dir))

    # 1) .ico varsa Windows class ikonu (title bar + görev çubuğu)
    for name in names:
        if name.lower().endswith(".ico"):
            try:
                root.iconbitmap(os.path.join(logo_dir, name))
                return
            except Exception:
                break

    # 2) .ico yoksa PNG/gif/jpg dosyasını doğrudan PhotoImage ile kullan
    for name in names:
        if name.lower().endswith((".png", ".gif", ".jpg", ".jpeg")):
            try:
                icon = tk.PhotoImage(file=os.path.join(logo_dir, name))
                root.iconphoto(True, icon)
                root._app_icon_photo = icon  # GC'den korumak için referans tut
                return
            except Exception:
                continue

# --------------------------------------------------------------------------
# Arayüz çevirileri
# --------------------------------------------------------------------------
UI = {
    "tr": {
        "title": "CV Oluşturucu — 10 Şablon",
        "file_menu": "Dosya",
        "save_draft": "Taslağı Kaydet (JSON)...",
        "load_draft": "Taslak Yükle (JSON)...",
        "exit": "Çıkış",
        "language": "Dil / Language:",
        "tr": "Türkçe",
        "en": "English",
        "personal_info": "Kişisel Bilgiler",
        "full_name": "Ad Soyad*:",
        "job_title": "Ünvan / Pozisyon:",
        "email": "E-posta:",
        "phone": "Telefon:",
        "address": "Adres / Şehir:",
        "linkedin": "LinkedIn:",
        "github": "GitHub:",
        "website": "Web Sitesi:",
        "summary": "Profil Özeti",
        "experience": "İş Deneyimi",
        "add_experience": "+ Deneyim Ekle",
        "education": "Eğitim",
        "add_education": "+ Eğitim Ekle",
        "skills": "Yetenekler",
        "languages": "Diller",
        "certifications": "Sertifikalar",
        "add": "Ekle",
        "remove_selected": "Seçileni Sil",
        "placeholder_example": "Örn: Python",
        "template_selection": "Şablon Seçimi (10 farklı tasarım)",
        "generate_pdf": "PDF CV Oluştur",
        "exp_record": "İş Deneyimi Kaydı",
        "edu_record": "Eğitim Kaydı",
        "exp_position": "Pozisyon / Ünvan",
        "exp_company": "Şirket",
        "exp_start": "Başlangıç (ör. 2022)",
        "exp_end": "Bitiş (boş bırakılırsa 'Devam ediyor')",
        "edu_degree": "Bölüm / Derece",
        "edu_school": "Okul / Üniversite",
        "edu_start": "Başlangıç",
        "edu_end": "Bitiş",
        "exp_desc": "Açıklama (her satır ayrı madde olarak eklenir):",
        "edu_desc": "Açıklama (her satır ayrı madde olarak eklenir):",
        "delete_record": "Bu Kaydı Sil",
        "warn_name": "Lütfen en azından 'Ad Soyad' alanını doldurun.",
        "save_pdf_title": "PDF CV'yi Kaydet",
        "pdf_file": "PDF Dosyası",
        "generated": "Oluşturuldu: {}",
        "ask_open": "CV başarıyla oluşturuldu. Şimdi açılsın mı?",
        "pdf_error": "PDF oluşturulurken bir hata oluştu:\n{}",
        "save_draft_title": "Taslağı Kaydet",
        "json_file": "JSON Dosyası",
        "draft_saved": "Taslak kaydedildi: {}",
        "draft_save_error": "Taslak kaydedilemedi:\n{}",
        "load_draft_title": "Taslak Yükle",
        "draft_load_error": "Taslak yüklenemedi:\n{}",
        "draft_loaded": "Taslak yüklendi: {}",
    },
    "en": {
        "title": "CV Builder — 10 Templates",
        "file_menu": "File",
        "save_draft": "Save Draft (JSON)...",
        "load_draft": "Load Draft (JSON)...",
        "exit": "Exit",
        "language": "Language:",
        "tr": "Türkçe",
        "en": "English",
        "personal_info": "Personal Information",
        "full_name": "Full Name*:",
        "job_title": "Job Title / Position:",
        "email": "Email:",
        "phone": "Phone:",
        "address": "Address / City:",
        "linkedin": "LinkedIn:",
        "github": "GitHub:",
        "website": "Website:",
        "summary": "Professional Summary",
        "experience": "Work Experience",
        "add_experience": "+ Add Experience",
        "education": "Education",
        "add_education": "+ Add Education",
        "skills": "Skills",
        "languages": "Languages",
        "certifications": "Certifications",
        "add": "Add",
        "remove_selected": "Remove Selected",
        "placeholder_example": "e.g. Python",
        "template_selection": "Template Selection (10 different designs)",
        "generate_pdf": "Generate PDF CV",
        "exp_record": "Work Experience Entry",
        "edu_record": "Education Entry",
        "exp_position": "Position / Title",
        "exp_company": "Company",
        "exp_start": "Start (e.g. 2022)",
        "exp_end": "End (leave empty for 'Present')",
        "edu_degree": "Degree / Field",
        "edu_school": "School / University",
        "edu_start": "Start",
        "edu_end": "End",
        "exp_desc": "Description (each line becomes a bullet point):",
        "edu_desc": "Description (each line becomes a bullet point):",
        "delete_record": "Delete This Entry",
        "warn_name": "Please fill in at least the 'Full Name' field.",
        "save_pdf_title": "Save PDF CV",
        "pdf_file": "PDF File",
        "generated": "Generated: {}",
        "ask_open": "CV created successfully. Open it now?",
        "pdf_error": "An error occurred while generating the PDF:\n{}",
        "save_draft_title": "Save Draft",
        "json_file": "JSON File",
        "draft_saved": "Draft saved: {}",
        "draft_save_error": "Could not save draft:\n{}",
        "load_draft_title": "Load Draft",
        "draft_load_error": "Could not load draft:\n{}",
        "draft_loaded": "Draft loaded: {}",
    },
}


class ScrollableFrame(ttk.Frame):
    """Fare tekerleği ile kaydırılabilen dikey scroll alanı."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   # Windows / macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)     # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)     # Linux scroll down

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")


class TaggedListEditor(ttk.Frame):
    """Yetenekler / Diller / Sertifikalar gibi basit liste alanları için
    ekle-sil arayüzü. Dil değişince etiketleri günceller."""

    def __init__(self, parent, placeholder_key, app):
        super().__init__(parent)
        self.app = app
        self.placeholder_key = placeholder_key
        self.entry_var = tk.StringVar()
        row = ttk.Frame(self)
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=self.entry_var)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self.add_item())
        self.add_btn = ttk.Button(row, command=self.add_item, width=8)
        self.add_btn.pack(side="left", padx=(6, 0))
        self.del_btn = ttk.Button(row, command=self.remove_selected)
        self.del_btn.pack(side="left", padx=(6, 0))

        self.listbox = tk.Listbox(self, height=4, exportselection=False)
        self.listbox.pack(fill="x", pady=(4, 0))
        self.update_texts()

    def update_texts(self):
        self.add_btn.config(text=self.app.t("add"))
        self.del_btn.config(text=self.app.t("remove_selected"))

    def add_item(self):
        val = self.entry_var.get().strip()
        if val:
            self.listbox.insert("end", val)
            self.entry_var.set("")

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        for idx in reversed(sel):
            self.listbox.delete(idx)

    def get_items(self):
        return list(self.listbox.get(0, "end"))

    def set_items(self, items):
        self.listbox.delete(0, "end")
        for it in items or []:
            self.listbox.insert("end", it)


class EntryRow:
    """İş deneyimi / eğitim için tek bir kayıt satırı (silinebilir kutu)."""

    FIELDS_EXPERIENCE = [
        ("company", "exp_company"),
        ("position", "exp_position"),
        ("start", "exp_start"),
        ("end", "exp_end"),
    ]
    FIELDS_EDUCATION = [
        ("degree", "edu_degree"),
        ("school", "edu_school"),
        ("start", "edu_start"),
        ("end", "edu_end"),
    ]

    def __init__(self, container, kind, on_delete, app):
        self.app = app
        self.kind = kind
        self.on_delete_cb = on_delete
        fields = self.FIELDS_EXPERIENCE if kind == "experience" else self.FIELDS_EDUCATION
        self.frame = ttk.LabelFrame(container)
        self.frame.pack(fill="x", pady=6, padx=2)
        self.vars = {}
        self.labels = []
        self.desc_label = None
        self.del_btn = None
        self.desc_text = None

        grid = ttk.Frame(self.frame)
        grid.pack(fill="x", padx=8, pady=(8, 4))
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        r = 0
        for i, (key, label_key) in enumerate(fields):
            col = (i % 2) * 2
            if i % 2 == 0 and i > 0:
                r += 1
            lbl = ttk.Label(grid)
            lbl.grid(row=r, column=col, sticky="w", padx=4, pady=3)
            self.labels.append(lbl)
            var = tk.StringVar()
            ttk.Entry(grid, textvariable=var).grid(row=r, column=col + 1, sticky="ew", padx=4, pady=3)
            self.vars[key] = var

        self.desc_label = ttk.Label(self.frame)
        self.desc_label.pack(anchor="w", padx=8)
        self.desc_text = tk.Text(self.frame, height=3, wrap="word")
        self.desc_text.pack(fill="x", padx=8, pady=(2, 8))

        self.del_btn = ttk.Button(self.frame, command=self._delete)
        self.del_btn.pack(anchor="e", padx=8, pady=(0, 8))

        self.key_fields = [key for key, _ in fields]
        self.update_texts()

    def _delete(self):
        self.on_delete_cb(self)

    def update_texts(self):
        is_exp = self.kind == "experience"
        self.frame.config(text=self.app.t("exp_record") if is_exp else self.app.t("edu_record"))
        fields = self.FIELDS_EXPERIENCE if is_exp else self.FIELDS_EDUCATION
        for i, (key, label_key) in enumerate(fields):
            if i < len(self.labels):
                self.labels[i].config(text=self.app.t(label_key) + ":")
        if self.desc_label:
            self.desc_label.config(
                text=self.app.t("exp_desc") if is_exp else self.app.t("edu_desc")
            )
        if self.del_btn:
            self.del_btn.config(text=self.app.t("delete_record"))

    def get_data(self):
        d = {k: v.get().strip() for k, v in self.vars.items()}
        d["description"] = self.desc_text.get("1.0", "end").strip()
        return d

    def set_data(self, d):
        for k, v in self.vars.items():
            v.set(d.get(k, ""))
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", d.get("description", ""))

    def destroy(self):
        self.frame.destroy()


class CVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = tk.StringVar(value="tr")
        self.title(APP_TITLE)
        self.geometry("880x760")
        self.minsize(680, 560)

        # uygulama ikonu: logos/ klasöründeki resmi görev çubuğu/title bar ikonu yapar
        set_app_icon(self)

        self._build_menu()
        self._build_layout()
        self.apply_language()

    def t(self, key):
        lang = self.language.get()
        return UI.get(lang, UI["tr"]).get(key, key)

    # ------------------------------------------------------------------
    # Arayüz kurulumu
    # ------------------------------------------------------------------

    def _build_menu(self):
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label=self.t("save_draft"), command=self.save_draft)
        self.filemenu.add_command(label=self.t("load_draft"), command=self.load_draft)
        self.filemenu.add_separator()
        self.filemenu.add_command(label=self.t("exit"), command=self.destroy)
        self.menubar.add_cascade(label=self.t("file_menu"), menu=self.filemenu)
        self.config(menu=self.menubar)

    def _build_layout(self):
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)

        scroll = ScrollableFrame(outer)
        scroll.pack(fill="both", expand=True, side="top")
        form = scroll.inner

        pad = {"padx": 10, "pady": 6}

        # --- Dil Seçimi ---------------------------------------------------
        lang_frame = ttk.LabelFrame(form)
        lang_frame.pack(fill="x", **pad)
        self.lang_label = ttk.Label(lang_frame)
        self.lang_label.pack(side="left", padx=8, pady=6)
        ttk.Radiobutton(lang_frame, text="Türkçe", value="tr",
                        variable=self.language, command=self.apply_language).pack(
            side="left", padx=(0, 12))
        ttk.Radiobutton(lang_frame, text="English", value="en",
                        variable=self.language, command=self.apply_language).pack(
            side="left")

        # --- Kişisel Bilgiler -------------------------------------------------
        personal = ttk.LabelFrame(form)
        personal.pack(fill="x", **pad)
        personal.columnconfigure(1, weight=1)
        personal.columnconfigure(3, weight=1)
        self.personal_frame = personal

        self.v_name = tk.StringVar()
        self.v_title = tk.StringVar()
        self.v_email = tk.StringVar()
        self.v_phone = tk.StringVar()
        self.v_address = tk.StringVar()
        self.v_linkedin = tk.StringVar()
        self.v_github = tk.StringVar()
        self.v_website = tk.StringVar()

        self.personal_labels = []
        rows = [
            ("full_name", self.v_name, 0, 0),
            ("job_title", self.v_title, 0, 2),
            ("email", self.v_email, 1, 0),
            ("phone", self.v_phone, 1, 2),
            ("address", self.v_address, 2, 0),
            ("linkedin", self.v_linkedin, 2, 2),
            ("github", self.v_github, 3, 0),
            ("website", self.v_website, 3, 2),
        ]
        self.personal_key_rows = []
        for key, var, r, c in rows:
            lbl = ttk.Label(personal)
            lbl.grid(row=r, column=c, sticky="w", padx=6, pady=4)
            self.personal_labels.append(lbl)
            self.personal_key_rows.append((key, lbl))
            ttk.Entry(personal, textvariable=var).grid(row=r, column=c + 1, sticky="ew", padx=6, pady=4)

        # --- Profil Özeti -------------------------------------------------
        summary_frame = ttk.LabelFrame(form)
        summary_frame.pack(fill="x", **pad)
        self.summary_text = tk.Text(summary_frame, height=4, wrap="word")
        self.summary_text.pack(fill="x", padx=8, pady=8)
        self.summary_frame = summary_frame

        # --- İş Deneyimi -------------------------------------------------
        exp_outer = ttk.LabelFrame(form)
        exp_outer.pack(fill="x", **pad)
        self.exp_container = ttk.Frame(exp_outer)
        self.exp_container.pack(fill="x")
        self.add_exp_btn = ttk.Button(exp_outer, command=self.add_experience)
        self.add_exp_btn.pack(anchor="w", padx=8, pady=(0, 8))
        self.experience_rows = []
        self.exp_outer = exp_outer

        # --- Eğitim -------------------------------------------------
        edu_outer = ttk.LabelFrame(form)
        edu_outer.pack(fill="x", **pad)
        self.edu_container = ttk.Frame(edu_outer)
        self.edu_container.pack(fill="x")
        self.add_edu_btn = ttk.Button(edu_outer, command=self.add_education)
        self.add_edu_btn.pack(anchor="w", padx=8, pady=(0, 8))
        self.education_rows = []
        self.edu_outer = edu_outer

        # --- Yetenekler / Diller / Sertifikalar ------------------------
        triple = ttk.Frame(form)
        triple.pack(fill="x", **pad)
        triple.columnconfigure(0, weight=1)
        triple.columnconfigure(1, weight=1)
        triple.columnconfigure(2, weight=1)

        skills_frame = ttk.LabelFrame(triple)
        skills_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.skills_editor = TaggedListEditor(skills_frame, "skills", self)
        self.skills_editor.pack(fill="x", padx=6, pady=6)
        self.skills_frame = skills_frame

        lang_frame2 = ttk.LabelFrame(triple)
        lang_frame2.grid(row=0, column=1, sticky="nsew", padx=6)
        self.lang_editor = TaggedListEditor(lang_frame2, "languages", self)
        self.lang_editor.pack(fill="x", padx=6, pady=6)
        self.lang_frame2 = lang_frame2

        cert_frame = ttk.LabelFrame(triple)
        cert_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        self.cert_editor = TaggedListEditor(cert_frame, "certifications", self)
        self.cert_editor.pack(fill="x", padx=6, pady=6)
        self.cert_frame = cert_frame

        # --- Şablon Seçimi -------------------------------------------------
        tmpl_frame = ttk.LabelFrame(form)
        tmpl_frame.pack(fill="x", **pad)
        self.template_var = tk.StringVar(value=TEMPLATES[0]["id"])

        self.tmpl_label = ttk.Label(tmpl_frame)
        self.tmpl_label.pack(anchor="w", padx=8, pady=(8, 0))

        grid = ttk.Frame(tmpl_frame)
        grid.pack(fill="x", padx=8, pady=8)
        for i, t in enumerate(TEMPLATES):
            r, c = divmod(i, 2)
            box = ttk.Frame(grid, relief="groove", borderwidth=1)
            box.grid(row=r, column=c, sticky="ew", padx=5, pady=4)
            grid.columnconfigure(c, weight=1)
            ttk.Radiobutton(
                box, text=t["name"], value=t["id"], variable=self.template_var
            ).pack(anchor="w", padx=6, pady=(4, 0))
            ttk.Label(box, text=t["desc"], foreground="#666666", wraplength=340).pack(
                anchor="w", padx=24, pady=(0, 4)
            )
        self.tmpl_frame = tmpl_frame

        # --- Alt bar: PDF oluştur -------------------------------------------------
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", side="bottom")
        ttk.Separator(bottom).pack(fill="x")
        btn_row = ttk.Frame(bottom)
        btn_row.pack(fill="x", padx=10, pady=10)
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(btn_row, textvariable=self.status_var, foreground="#2a7a2a")
        self.status_label.pack(side="left")
        self.generate_btn = ttk.Button(btn_row, command=self.generate_pdf)
        self.generate_btn.pack(side="right")

        # başlangıçta bir deneyim ve bir eğitim satırı ekle
        self.add_experience()
        self.add_education()

    def apply_language(self):
        """Arayüz etiketlerini seçilen dile göre günceller."""
        lang = self.language.get()
        self.title(UI[lang]["title"])

        # menüyü yeniden oluştur
        self.config(menu=None)
        self._build_menu()

        # dil seçimi
        self.lang_label.config(text=self.t("language"))

        # kişisel bilgiler
        self.personal_frame.config(text=self.t("personal_info"))
        for key, lbl in self.personal_key_rows:
            lbl.config(text=self.t(key) + ":")

        # profil özeti
        self.summary_frame.config(text=self.t("summary"))

        # iş deneyimi / eğitim
        self.exp_outer.config(text=self.t("experience"))
        self.add_exp_btn.config(text=self.t("add_experience"))
        self.edu_outer.config(text=self.t("education"))
        self.add_edu_btn.config(text=self.t("add_education"))

        # yetenekler / diller / sertifikalar
        self.skills_frame.config(text=self.t("skills"))
        self.lang_frame2.config(text=self.t("languages"))
        self.cert_frame.config(text=self.t("certifications"))
        self.skills_editor.update_texts()
        self.lang_editor.update_texts()
        self.cert_editor.update_texts()

        # şablon seçimi
        self.tmpl_frame.config(text=self.t("template_selection"))

        # alt bar
        self.generate_btn.config(text=self.t("generate_pdf"))

        # dinamik satırlar
        for row in self.experience_rows:
            row.update_texts()
        for row in self.education_rows:
            row.update_texts()

    # ------------------------------------------------------------------
    # Dinamik satır yönetimi
    # ------------------------------------------------------------------

    def add_experience(self, data=None):
        row = EntryRow(self.exp_container, "experience", self._delete_experience, self)
        if data:
            row.set_data(data)
        self.experience_rows.append(row)

    def _delete_experience(self, row):
        if row in self.experience_rows:
            self.experience_rows.remove(row)
        row.destroy()

    def add_education(self, data=None):
        row = EntryRow(self.edu_container, "education", self._delete_education, self)
        if data:
            row.set_data(data)
        self.education_rows.append(row)

    def _delete_education(self, row):
        if row in self.education_rows:
            self.education_rows.remove(row)
        row.destroy()

    # ------------------------------------------------------------------
    # Veri toplama / PDF üretme
    # ------------------------------------------------------------------

    def collect_data(self):
        data = {
            "language": self.language.get(),
            "full_name": self.v_name.get().strip(),
            "job_title": self.v_title.get().strip(),
            "email": self.v_email.get().strip(),
            "phone": self.v_phone.get().strip(),
            "address": self.v_address.get().strip(),
            "linkedin": self.v_linkedin.get().strip(),
            "github": self.v_github.get().strip(),
            "website": self.v_website.get().strip(),
            "summary": self.summary_text.get("1.0", "end").strip(),
            "experience": [r.get_data() for r in self.experience_rows
                            if any(r.get_data().values())],
            "education": [r.get_data() for r in self.education_rows
                           if any(r.get_data().values())],
            "skills": self.skills_editor.get_items(),
            "languages": self.lang_editor.get_items(),
            "certifications": self.cert_editor.get_items(),
        }
        return data

    def generate_pdf(self):
        data = self.collect_data()
        if not data["full_name"]:
            messagebox.showwarning(self.t("title"), self.t("warn_name"))
            return

        default_name = (data["full_name"].replace(" ", "_") or "CV") + "_CV.pdf"
        path = filedialog.asksaveasfilename(
            title=self.t("save_pdf_title"),
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[(self.t("pdf_file"), "*.pdf")],
        )
        if not path:
            return

        try:
            generate_cv_pdf(self.template_var.get(), data, path)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(self.t("title"), self.t("pdf_error").format(e))
            return

        self.status_var.set(self.t("generated").format(os.path.basename(path)))
        if messagebox.askyesno(self.t("title"), self.t("ask_open")):
            self._open_file(path)

    @staticmethod
    def _open_file(path):
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Taslak kaydet / yükle
    # ------------------------------------------------------------------

    def save_draft(self):
        data = self.collect_data()
        data["_template"] = self.template_var.get()
        path = filedialog.asksaveasfilename(
            title=self.t("save_draft_title"), defaultextension=".json",
            filetypes=[(self.t("json_file"), "*.json")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set(self.t("draft_saved").format(os.path.basename(path)))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(self.t("title"), self.t("draft_save_error").format(e))

    def load_draft(self):
        path = filedialog.askopenfilename(
            title=self.t("load_draft_title"), filetypes=[(self.t("json_file"), "*.json")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(self.t("title"), self.t("draft_load_error").format(e))
            return

        # Dil
        if data.get("language"):
            self.language.set(data["language"])
            self.apply_language()

        self.v_name.set(data.get("full_name", ""))
        self.v_title.set(data.get("job_title", ""))
        self.v_email.set(data.get("email", ""))
        self.v_phone.set(data.get("phone", ""))
        self.v_address.set(data.get("address", ""))
        self.v_linkedin.set(data.get("linkedin", ""))
        self.v_github.set(data.get("github", ""))
        self.v_website.set(data.get("website", ""))
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", data.get("summary", ""))

        for row in list(self.experience_rows):
            self._delete_experience(row)
        for exp in data.get("experience", []):
            self.add_experience(exp)

        for row in list(self.education_rows):
            self._delete_education(row)
        for edu in data.get("education", []):
            self.add_education(edu)

        self.skills_editor.set_items(data.get("skills", []))
        self.lang_editor.set_items(data.get("languages", []))
        self.cert_editor.set_items(data.get("certifications", []))

        if data.get("_template"):
            self.template_var.set(data["_template"])

        self.status_var.set(self.t("draft_loaded").format(os.path.basename(path)))


def main():
    app = CVApp()
    app.mainloop()


if __name__ == "__main__":
    main()