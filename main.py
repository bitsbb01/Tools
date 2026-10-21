from __future__ import annotations

import queue
import shutil
import subprocess
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
import sys
from tkinter import filedialog, messagebox, ttk

from media_tools import RESOLUTIONS, build_ffmpeg_command, parse_time


APP_NAME = "JGJG Video Studio"


def find_ffmpeg() -> str | None:
    """Use the bundled FFmpeg first, then allow a developer PATH install."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled = Path(sys._MEIPASS) / "ffmpeg" / "ffmpeg.exe"
        if bundled.is_file():
            return str(bundled)
    return shutil.which("ffmpeg")


class VideoStudio(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("760x650")
        self.minsize(680, 590)
        self.configure(bg="#10151d")
        self.proc: subprocess.Popen[str] | None = None
        self.cancel_requested = False
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.source = tk.StringVar()
        self.output = tk.StringVar()
        self.music = tk.StringVar()
        self.start = tk.StringVar(value="00:00:00")
        self.duration = tk.StringVar(value="00:00:10")
        self.resolution = tk.StringVar(value="Original")
        self.status = tk.StringVar(value="Ready — processing stays on this computer.")
        self._style()
        self._build()
        self.after(100, self._check_events)

    def _style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#10151d")
        style.configure("Card.TFrame", background="#19212c")
        style.configure("TLabel", background="#10151d", foreground="#eef2f6", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#19212c", foreground="#eef2f6", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground="#f4c66a")
        style.configure("Sub.TLabel", foreground="#aab6c5")
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Accent.TButton", background="#d69d42", foreground="#151515", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#efbd63")])
        style.configure("TEntry", fieldbackground="#0d1117", foreground="#eef2f6", insertcolor="#eef2f6")
        style.configure("TCombobox", fieldbackground="#0d1117", foreground="#eef2f6")
        style.configure("Horizontal.TProgressbar", troughcolor="#283342", background="#d69d42")

    def _build(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="JGJG Video Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Free local video tools · Your files stay on your computer", style="Sub.TLabel").pack(anchor="w", pady=(3, 18))

        card = ttk.Frame(root, style="Card.TFrame", padding=18)
        card.pack(fill="x")
        self._file_row(card, "Video file", self.source, self._choose_source, 0)
        self._file_row(card, "Export MP4 to", self.output, self._choose_output, 1)
        self._file_row(card, "Replace audio with music (optional)", self.music, self._choose_music, 2)

        options = ttk.Frame(root, style="Card.TFrame", padding=18)
        options.pack(fill="x", pady=14)
        ttk.Label(options, text="Edit settings", style="Card.TLabel", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))
        ttk.Label(options, text="Start at", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Entry(options, textvariable=self.start, width=18).grid(row=2, column=0, sticky="w", pady=(4, 0), padx=(0, 18))
        ttk.Label(options, text="Clip length", style="Card.TLabel").grid(row=1, column=1, sticky="w")
        ttk.Entry(options, textvariable=self.duration, width=18).grid(row=2, column=1, sticky="w", pady=(4, 0), padx=(0, 18))
        ttk.Label(options, text="Output size", style="Card.TLabel").grid(row=1, column=2, sticky="w")
        ttk.Combobox(options, textvariable=self.resolution, values=list(RESOLUTIONS), state="readonly", width=23).grid(row=2, column=2, sticky="w", pady=(4, 0))
        ttk.Label(options, text="Time accepts seconds or HH:MM:SS. Resizing fits the full image without cropping.", style="Card.TLabel").grid(row=3, column=0, columnspan=4, sticky="w", pady=(12, 0))

        row = ttk.Frame(root)
        row.pack(fill="x", pady=(2, 8))
        self.export_btn = ttk.Button(row, text="Export video", style="Accent.TButton", command=self.export)
        self.export_btn.pack(side="left")
        self.cancel_btn = ttk.Button(row, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_btn.pack(side="left", padx=8)
        ttk.Button(row, text="FFmpeg license info", command=lambda: webbrowser.open("https://ffmpeg.org/legal.html")).pack(side="left")
        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 8))
        ttk.Label(root, textvariable=self.status, style="Sub.TLabel").pack(anchor="w")
        ttk.Label(root, text="Created by JGJG Books · FFmpeg is included with the Windows app.", style="Sub.TLabel").pack(side="bottom", anchor="w", pady=(18, 0))

    def _file_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, callback, row: int) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row * 2, column=0, sticky="w", pady=(0 if row == 0 else 12, 4))
        ttk.Entry(parent, textvariable=variable).grid(row=row * 2 + 1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(parent, text="Browse…", command=callback).grid(row=row * 2 + 1, column=1, sticky="e")
        parent.columnconfigure(0, weight=1)

    def _choose_source(self) -> None:
        path = filedialog.askopenfilename(title="Choose a video", filetypes=[("Video files", "*.mp4 *.mov *.mkv *.webm *.avi"), ("All files", "*.*")])
        if path:
            self.source.set(path)
            self.output.set(str(Path(path).with_name(Path(path).stem + "-edited.mp4")))

    def _choose_output(self) -> None:
        path = filedialog.asksaveasfilename(title="Export MP4", defaultextension=".mp4", filetypes=[("MP4 video", "*.mp4")])
        if path:
            self.output.set(path)

    def _choose_music(self) -> None:
        path = filedialog.askopenfilename(title="Choose music or audio", filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.aac *.ogg *.flac"), ("All files", "*.*")])
        if path:
            self.music.set(path)

    def export(self) -> None:
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            messagebox.showerror("FFmpeg is missing", "The bundled FFmpeg files were not found. Reinstall JGJG Video Studio.")
            return
        try:
            start = parse_time(self.start.get())
            duration = parse_time(self.duration.get())
            if not self.output.get().strip():
                raise ValueError("Choose where to save the MP4.")
            command = build_ffmpeg_command(ffmpeg, self.source.get(), self.output.get(), start, duration, self.resolution.get(), self.music.get() or None)
        except ValueError as exc:
            messagebox.showerror("Check the edit settings", str(exc))
            return
        Path(self.output.get()).parent.mkdir(parents=True, exist_ok=True)
        self.export_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.cancel_requested = False
        self.progress.configure(value=0)
        self.status.set("Exporting… the source file will not be changed.")
        threading.Thread(target=self._run_export, args=(command, duration), daemon=True).start()

    def _run_export(self, command: list[str], duration: float) -> None:
        try:
            self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding="utf-8", errors="replace")
            assert self.proc.stdout is not None
            for line in self.proc.stdout:
                if line.startswith("out_time_ms="):
                    try:
                        seconds = int(line.split("=", 1)[1]) / 1_000_000
                        self.events.put(("progress", min(99, seconds / duration * 100)))
                    except ValueError:
                        pass
            code = self.proc.wait()
            if code == 0:
                self.events.put(("done", command[-1]))
            elif self.cancel_requested:
                self.events.put(("cancelled", "Export cancelled. The source video was not changed."))
            else:
                self.events.put(("error", f"FFmpeg exited with code {code}. Check that the clip and audio files are supported and that the output path is writable."))
        except Exception as exc:
            self.events.put(("error", str(exc)))
        finally:
            self.proc = None

    def cancel(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.cancel_requested = True
            self.proc.terminate()
            self.status.set("Cancelling export…")

    def _check_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "progress":
                    self.progress.configure(value=value)
                elif kind == "done":
                    self.progress.configure(value=100)
                    self.status.set(f"Export complete: {value}")
                    self.export_btn.configure(state="normal")
                    self.cancel_btn.configure(state="disabled")
                    messagebox.showinfo("Export complete", f"Your video was saved to:\n{value}")
                elif kind == "error":
                    self.status.set("Export failed.")
                    self.export_btn.configure(state="normal")
                    self.cancel_btn.configure(state="disabled")
                    messagebox.showerror("Export failed", str(value))
                elif kind == "cancelled":
                    self.progress.configure(value=0)
                    self.status.set(str(value))
                    self.export_btn.configure(state="normal")
                    self.cancel_btn.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._check_events)


if __name__ == "__main__":
    VideoStudio().mainloop()
