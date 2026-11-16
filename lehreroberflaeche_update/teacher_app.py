"""Teacher launcher, source-mode preview. Run from the project: python teacher_app.py."""
from __future__ import annotations
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Abhaengigkeit fehlt", "Pillow fehlt. Im Projektordner ausfuehren:\npython -m pip install -r requirements-teacher.txt")
    root.destroy()
    raise SystemExit(1)
from teacher_backend import (VERSION, data_home, read_json, prepare_run, detector_command,
                             validate_result, viewer_command, friendly_error)

PROJECT = Path(__file__).resolve().parent


def open_local(path: Path):
    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class TeacherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mittelalterliche Stadt – Lehrkraft | " + VERSION)
        self.geometry("1100x800")
        self.minsize(800, 620)
        self.events = queue.Queue()
        self.image_path = None
        self.run_dir = None
        self.city = None
        self.proc = None
        self.busy = False
        self.closing = threading.Event()
        self.preview_photo = None
        self.preview_image = None
        self.resize_job = None
        self.config_path = data_home() / "teacher_settings.json"
        self.godot_path = None
        try:
            value = read_json(self.config_path).get("godot", "")
            if value:
                self.godot_path = Path(value)
        except (OSError, ValueError, AttributeError):
            pass
        if self.godot_path is None:
            found = shutil.which("godot") or shutil.which("godot4")
            candidates = sorted(PROJECT.glob("Godot*.exe"))
            if found:
                self.godot_path = Path(found)
            elif candidates:
                self.godot_path = next((p for p in candidates if "console" not in p.name.lower()), candidates[0])
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.after(100, self.poll)

    def build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        top = ttk.Frame(self, padding=12)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Mittelalterliche Stadt", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(top, text="1. Foto waehlen   →   2. Erkennen   →   3. Kontrollieren   →   4. 3D-Stadt oeffnen").pack(anchor="w", pady=(5, 0))
        buttons = ttk.Frame(self, padding=(12, 0, 12, 8))
        buttons.grid(row=1, column=0, sticky="ew")
        self.choose_btn = ttk.Button(buttons, text="Bild auswaehlen …", command=self.choose_image)
        self.choose_btn.pack(side="left")
        self.detect_btn = ttk.Button(buttons, text="Stadt erkennen", command=self.detect, state="disabled")
        self.detect_btn.pack(side="left", padx=8)
        self.view_btn = ttk.Button(buttons, text="3D-Stadt oeffnen", command=self.launch_viewer, state="disabled")
        self.view_btn.pack(side="left")
        self.godot_btn = ttk.Button(buttons, text="Godot auswaehlen …", command=self.choose_godot)
        self.godot_btn.pack(side="right")
        panel = ttk.Frame(self, padding=(12, 0, 12, 0))
        panel.grid(row=2, column=0, sticky="nsew")
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)
        self.filename = tk.StringVar(value="Noch kein Foto ausgewaehlt.")
        ttk.Label(panel, textvariable=self.filename, wraplength=1000).grid(row=0, column=0, sticky="w", pady=5)
        self.preview = tk.Canvas(panel, background="#dedbd3", highlightthickness=0)
        self.preview.grid(row=1, column=0, sticky="nsew")
        self.preview.create_text(350, 150, text="Hier erscheinen Foto und Kontrollbild.", fill="#444444")
        self.preview.bind("<Configure>", self.schedule_render)
        self.preview.bind("<Double-Button-1>", lambda event: self.open_control())
        lower = ttk.Frame(self, padding=12)
        lower.grid(row=3, column=0, sticky="ew")
        self.status = tk.StringVar(value="Bereit. Beim ersten Start gegebenenfalls Godot auswaehlen.")
        ttk.Label(lower, textvariable=self.status, wraplength=1000).pack(anchor="w")
        self.progress = ttk.Progressbar(lower, mode="indeterminate")
        self.progress.pack(fill="x", pady=5)
        self.warnings = tk.Text(lower, height=5, wrap="word", state="disabled")
        self.warnings.pack(fill="x")
        foot = ttk.Frame(lower)
        foot.pack(fill="x", pady=(8, 0))
        ttk.Button(foot, text="Ergebnisordner", command=self.open_results).pack(side="left")
        ttk.Button(foot, text="Protokoll", command=self.open_log).pack(side="left", padx=8)
        ttk.Button(foot, text="Hilfe", command=self.help).pack(side="right")
        self.preview_choice = tk.StringVar(value="rectified.jpg")
        self.mode_box = ttk.Combobox(foot, textvariable=self.preview_choice, state="readonly", width=20,
                                   values=["rectified.jpg", "control.jpg", "Originalfoto"])
        self.mode_box.pack(side="right", padx=10)
        self.mode_box.bind("<<ComboboxSelected>>", lambda e: self.select_preview())

    def set_notes(self, text):
        self.warnings.configure(state="normal")
        self.warnings.delete("1.0", "end")
        self.warnings.insert("1.0", text)
        self.warnings.configure(state="disabled")

    def set_busy(self, value):
        self.busy = value
        self.choose_btn.configure(state="disabled" if value else "normal")
        self.godot_btn.configure(state="disabled" if value else "normal")
        self.detect_btn.configure(state="normal" if not value and self.image_path else "disabled")
        self.view_btn.configure(state="normal" if not value and self.city else "disabled")
        if value:
            self.progress.start(12)
        else:
            self.progress.stop()

    def choose_image(self):
        name = filedialog.askopenfilename(title="Foto des Stadtblatts auswaehlen", filetypes=[
            ("Bilder", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"), ("Alle Dateien", "*.*")])
        if not name:
            return
        self.image_path = Path(name)
        self.city, self.run_dir = None, None
        self.set_busy(False)
        self.filename.set(str(self.image_path))
        self.set_notes("")
        self.status.set("Foto ausgewaehlt. Jetzt 'Stadt erkennen' druecken.")
        self.show_image(self.image_path)

    def show_image(self, path):
        try:
            with Image.open(path) as img:
                # Keep original pixel orientation, matching cv2.imdecode in detect_city.py.
                self.preview_image = img.convert("RGB")
            self.render()
        except Exception as exc:
            self.preview_image = None
            self.preview.delete("all")
            messagebox.showerror("Bild nicht lesbar", str(exc))

    def schedule_render(self, event=None):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(100, self.render)

    def render(self):
        self.resize_job = None
        if self.preview_image is None:
            return
        size = (max(20, self.preview.winfo_width()-12), max(20, self.preview.winfo_height()-12))
        image = ImageOps.contain(self.preview_image, size, Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(image)
        self.preview.delete("all")
        self.preview.create_image(self.preview.winfo_width()/2, self.preview.winfo_height()/2,
                                  image=self.preview_photo, anchor="center")

    def choose_godot(self):
        name = filedialog.askopenfilename(title="Godot-Editor-Programmdatei auswaehlen", filetypes=[
            ("Programme", "*.exe"), ("Alle Dateien", "*.*")])
        if name:
            self.godot_path = Path(name)
            try:
                self.config_path.write_text(json.dumps({"godot": str(self.godot_path)}, ensure_ascii=False, indent=2), encoding="utf-8")
                self.status.set("Godot gespeichert: " + self.godot_path.name)
            except OSError as exc:
                messagebox.showerror("Einstellung nicht gespeichert", str(exc))

    def detect(self):
        self.city = None
        self.run_dir = None
        self.set_busy(True)
        self.set_notes("")
        self.status.set("Stadt wird erkannt. Bitte warten …")
        image = self.image_path
        threading.Thread(target=self.detect_worker, args=(image,), daemon=True).start()

    def detect_worker(self, image):
        run = None
        try:
            run = prepare_run(PROJECT, image)
            self.events.put(("run", run))
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            with (run / "detect.log").open("w", encoding="utf-8") as log:
                cmd = detector_command(PROJECT, image, run)
                log.write("CityProject " + VERSION + "\n" + repr(cmd) + "\n")
                log.flush()
                if self.closing.is_set():
                    return
                self.proc = subprocess.Popen(cmd, cwd=str(PROJECT), env=env, stdout=log, stderr=subprocess.STDOUT,
                                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if self.closing.is_set():
                    self.proc.terminate()
                code = self.proc.wait()
                self.proc = None
            if code:
                raise RuntimeError(friendly_error((run / "detect.log").read_text(encoding="utf-8")))
            city = validate_result(run)
            self.events.put(("done", (run, city)))
        except Exception as exc:
            if run:
                with (run / "detect.log").open("a", encoding="utf-8") as log:
                    log.write("\nLAUNCHER\n" + traceback.format_exc())
            self.events.put(("error", str(exc)))

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "run":
                    self.run_dir = value
                elif kind == "done":
                    self.run_dir, self.city = value
                    self.set_busy(False)
                    issues = self.city.get("warnings", [])
                    self.set_notes("\n".join(issues) if issues else "Keine Warnungen gemeldet. Bitte trotzdem Lage, Anzahl und Tuerausrichtung visuell pruefen.")
                    self.status.set(f"{len(self.city['buildings'])} Gebaeude erkannt. Kontrollbild pruefen." + (" Warnungen beachten!" if issues else ""))
                    self.preview_choice.set("rectified.jpg")
                    self.select_preview()
                elif kind == "error":
                    self.set_busy(False)
                    self.status.set("Erkennung fehlgeschlagen. Vorherige Ergebnisse werden nicht verwendet.")
                    messagebox.showerror("Erkennung fehlgeschlagen", value)
        except queue.Empty:
            pass
        if not self.closing.is_set():
            self.after(100, self.poll)

    def select_preview(self):
        if self.preview_choice.get() == "Originalfoto" or not self.city:
            if self.image_path:
                self.show_image(self.image_path)
        elif self.run_dir:
            self.show_image(self.run_dir / "result" / self.preview_choice.get())

    def launch_viewer(self):
        if not self.city or not self.run_dir:
            return
        if not self.godot_path or not self.godot_path.is_file():
            self.choose_godot()
            if not self.godot_path or not self.godot_path.is_file():
                return
        if self.city.get("warnings") and not messagebox.askyesno("Warnungen vorhanden", "Die Erkennung meldet Warnungen, zum Beispiel Ueberlappungen.\nKontrollbild geprueft und trotzdem in 3D oeffnen?"):
            return
        try:
            cmd = viewer_command(PROJECT, self.godot_path, self.run_dir)
            with (self.run_dir / "viewer.log").open("a", encoding="utf-8") as log:
                log.write(repr(cmd) + "\n")
                log.flush()
                self.proc = subprocess.Popen(cmd, cwd=str(PROJECT), stdout=log, stderr=subprocess.STDOUT)
            self.set_busy(True)
            self.status.set("3D-Ansicht laeuft. Mit Esc schliessen und hierher zurueckkehren.")
            self.after(300, self.check_viewer)
        except Exception as exc:
            self.proc = None
            self.set_busy(False)
            messagebox.showerror("3D-Start fehlgeschlagen", str(exc))

    def check_viewer(self):
        if not self.proc or self.closing.is_set():
            return
        code = self.proc.poll()
        if code is None:
            self.after(300, self.check_viewer)
            return
        self.proc = None
        self.set_busy(False)
        self.status.set("3D-Ansicht geschlossen. Bereit fuer einen weiteren Start oder ein neues Foto.")
        if code:
            messagebox.showerror("Viewer beendet", "Godot wurde mit Fehlercode " + str(code) + " beendet. Details: Protokoll → viewer.log.")

    def open_results(self):
        try:
            open_local(self.run_dir if self.run_dir else data_home())
        except OSError as exc:
            messagebox.showerror("Ordner nicht geoeffnet", str(exc))

    def open_log(self):
        if self.run_dir and (self.run_dir / "detect.log").is_file():
            try:
                open_local(self.run_dir / "detect.log")
            except OSError as exc:
                messagebox.showerror("Protokoll nicht geoeffnet", str(exc))
        else:
            messagebox.showinfo("Protokoll", "Noch kein Erkennungsprotokoll vorhanden.")

    def open_control(self):
        if self.run_dir and self.city:
            try:
                open_local(self.run_dir / "result" / "rectified.jpg")
            except OSError as exc:
                messagebox.showerror("Kontrollbild", str(exc))

    def help(self):
        messagebox.showinfo("Hilfe", "Alle vier Eckmarker muessen sichtbar sein.\nFoto auswaehlen → Stadt erkennen → Kontrollbild pruefen → 3D-Stadt oeffnen.\n\nGodot wird einmal ueber 'Godot auswaehlen' eingerichtet.\n3D: WASD/Pfeile, Maus; V: Vogelperspektive; Esc: zurueck.\n\nDie Verarbeitung erfolgt lokal, ohne Upload. Originalfotos werden nicht kopiert.\nKontrollbilder, Stadtdaten und Protokolle bleiben im Ergebnisordner.\nDiesen bei Bedarf im Explorer loeschen, wenn keine Verarbeitung laeuft.\n\nDies ist die Python-Entwicklungsfassung, noch keine eigenstaendige EXE.")

    def close_app(self):
        if self.busy and not messagebox.askyesno("Beenden", "Verarbeitung oder 3D-Ansicht laeuft noch. Beenden und gestarteten Prozess schliessen?"):
            return
        self.closing.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.destroy()


if __name__ == "__main__":
    TeacherApp().mainloop()
