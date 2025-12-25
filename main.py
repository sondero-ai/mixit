"""
Mixit - Ultra Fast Video Mixer
Entry point & GUI using CustomTkinter
"""

import os
import sys
import threading
import webbrowser
import urllib.request
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from utils import get_video_files, get_audio_files
from mixer_engine import MixerEngine
from ffmpeg_helper import get_ffmpeg_path, get_ffprobe_path

# Version
VERSION = "1.1.0"
GITHUB_REPO = "sondero-ai/mixit"

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Translations
TRANSLATIONS = {
    "en": {
        "title": "Mixit Studio",
        "select_video": "Select Video Folder",
        "select_music": "Select Music Folder",
        "no_folder": "No folder selected (or drag & drop here)",
        "videos": "Videos",
        "music": "Music",
        "duration": "Duration (minutes):",
        "output_name": "Output Name:",
        "save_to": "Save To...",
        "smooth_audio": "Smooth Audio (crossfade)",
        "start": "START MIXING",
        "mixing": "MIXING...",
        "welcome": "Welcome to Mixit...",
        "found_videos": "Found {0} video files",
        "found_music": "Found {0} music files",
        "output_folder": "Output folder: {0}",
        "already_mixing": "Already mixing, please wait...",
        "error_no_video": "Please select a video folder",
        "error_no_video_files": "No video files found in selected folder",
        "error_duration": "Please enter a valid duration in minutes",
        "mode_copy": "Mode: INSTANT (Video Copy + Audio Copy)",
        "mode_crossfade": "Mode: INSTANT (Video Copy + Audio Crossfade)",
        "success": "SUCCESS! Mix created at: {0}",
        "error": "ERROR: {0}",
        "success_title": "Success",
        "success_msg": "Mix created successfully!",
        "error_title": "Error",
        "mix_failed": "Mixing failed:",
        "estimated_time": "Estimated time: {0}",
        "progress": "Progress: {0}%",
        "format": "Format:",
        "language": "Language:",
        "check_update": "Check Update",
        "new_version": "New version {0} available! Download now?",
        "no_update": "You're using the latest version.",
        "ffmpeg_missing": "FFmpeg not found!",
        "ffmpeg_guide": "FFmpeg is required. Would you like to open the download page?",
        "batch_mode": "Batch Mode",
        "add_to_batch": "Add to Batch",
        "clear_batch": "Clear Batch",
        "run_batch": "Run Batch ({0} jobs)",
        "batch_complete": "Batch complete! {0} mixes created.",
        "playlist_order": "Playlist Order:",
        "random": "Random",
        "alphabetical": "A-Z",
        "manual": "Manual...",
    },
    "id": {
        "title": "Mixit Studio",
        "select_video": "Pilih Folder Video",
        "select_music": "Pilih Folder Musik",
        "no_folder": "Belum ada folder (atau drag & drop ke sini)",
        "videos": "Video",
        "music": "Musik",
        "duration": "Durasi (menit):",
        "output_name": "Nama Output:",
        "save_to": "Simpan Ke...",
        "smooth_audio": "Audio Halus (crossfade)",
        "start": "MULAI MIXING",
        "mixing": "SEDANG MIXING...",
        "welcome": "Selamat datang di Mixit...",
        "found_videos": "Ditemukan {0} file video",
        "found_music": "Ditemukan {0} file musik",
        "output_folder": "Folder output: {0}",
        "already_mixing": "Sedang mixing, mohon tunggu...",
        "error_no_video": "Silakan pilih folder video",
        "error_no_video_files": "Tidak ada file video di folder yang dipilih",
        "error_duration": "Masukkan durasi yang valid dalam menit",
        "mode_copy": "Mode: INSTAN (Video Copy + Audio Copy)",
        "mode_crossfade": "Mode: INSTAN (Video Copy + Audio Crossfade)",
        "success": "SUKSES! Mix dibuat di: {0}",
        "error": "ERROR: {0}",
        "success_title": "Sukses",
        "success_msg": "Mix berhasil dibuat!",
        "error_title": "Error",
        "mix_failed": "Mixing gagal:",
        "estimated_time": "Estimasi waktu: {0}",
        "progress": "Progress: {0}%",
        "format": "Format:",
        "language": "Bahasa:",
        "check_update": "Cek Update",
        "new_version": "Versi baru {0} tersedia! Download sekarang?",
        "no_update": "Anda menggunakan versi terbaru.",
        "ffmpeg_missing": "FFmpeg tidak ditemukan!",
        "ffmpeg_guide": "FFmpeg diperlukan. Buka halaman download?",
        "batch_mode": "Mode Batch",
        "add_to_batch": "Tambah ke Batch",
        "clear_batch": "Hapus Batch",
        "run_batch": "Jalankan Batch ({0} job)",
        "batch_complete": "Batch selesai! {0} mix dibuat.",
        "playlist_order": "Urutan Playlist:",
        "random": "Acak",
        "alphabetical": "A-Z",
        "manual": "Manual...",
    }
}


class MixitApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.lang = "en"
        self.t = TRANSLATIONS[self.lang]
        
        self.title(f"{self.t['title']} v{VERSION}")
        self.geometry("620x720")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")
        
        self.video_folder = ""
        self.music_folder = ""
        self.output_folder = ""
        self.video_count = 0
        self.music_count = 0
        self.music_files = []
        
        self.engine = MixerEngine()
        self.is_mixing = False
        self.batch_jobs = []
        
        # Check FFmpeg on startup
        self._check_ffmpeg()
        
        self._create_widgets()
        self._log(self.t["welcome"])
        
        # Check for updates in background
        threading.Thread(target=self._check_update_silent, daemon=True).start()
    
    def _tr(self, key, *args):
        """Get translated string."""
        text = self.t.get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available."""
        try:
            get_ffmpeg_path()
            get_ffprobe_path()
        except FileNotFoundError:
            if messagebox.askyesno(self._tr("ffmpeg_missing"), self._tr("ffmpeg_guide")):
                webbrowser.open("https://www.gyan.dev/ffmpeg/builds/")
            sys.exit(1)

    def _create_widgets(self):
        # Main container with CTk styling
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === Top Bar (Language + Update) ===
        top_bar = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        # Language selector
        lang_label = ctk.CTkLabel(top_bar, text=self._tr("language"))
        lang_label.pack(side="left", padx=(0, 5))
        
        self.lang_var = ctk.StringVar(value="English")
        self.lang_menu = ctk.CTkOptionMenu(
            top_bar, values=["English", "Indonesia"], 
            variable=self.lang_var, width=100,
            command=self._change_language
        )
        self.lang_menu.pack(side="left")
        
        # Update button
        self.btn_update = ctk.CTkButton(
            top_bar, text=self._tr("check_update"), width=100,
            command=self._check_update
        )
        self.btn_update.pack(side="right")
        
        # === Video Folder Section (with drag & drop) ===
        video_frame = ctk.CTkFrame(main_frame)
        video_frame.pack(fill="x", pady=(0, 8))
        
        self.btn_video = ctk.CTkButton(
            video_frame, text=self._tr("select_video"), width=150,
            command=self._select_video_folder
        )
        self.btn_video.pack(side="left", padx=(10, 10), pady=10)
        
        self.lbl_video_path = ctk.CTkLabel(video_frame, text=self._tr("no_folder"), anchor="w")
        self.lbl_video_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Enable drag & drop for video frame
        video_frame.drop_target_register(DND_FILES)
        video_frame.dnd_bind('<<Drop>>', self._on_video_drop)
        
        # === Music Folder Section (with drag & drop) ===
        music_frame = ctk.CTkFrame(main_frame)
        music_frame.pack(fill="x", pady=(0, 8))
        
        self.btn_music = ctk.CTkButton(
            music_frame, text=self._tr("select_music"), width=150,
            command=self._select_music_folder
        )
        self.btn_music.pack(side="left", padx=(10, 10), pady=10)
        
        self.lbl_music_path = ctk.CTkLabel(music_frame, text=self._tr("no_folder"), anchor="w")
        self.lbl_music_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Enable drag & drop for music frame
        music_frame.drop_target_register(DND_FILES)
        music_frame.dnd_bind('<<Drop>>', self._on_music_drop)
        
        # === Stats Section ===
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=(0, 8))
        
        self.lbl_video_count = ctk.CTkLabel(stats_frame, text=f"{self._tr('videos')}: 0")
        self.lbl_video_count.pack(side="left", padx=20, pady=10)
        
        self.lbl_music_count = ctk.CTkLabel(stats_frame, text=f"{self._tr('music')}: 0")
        self.lbl_music_count.pack(side="left", padx=20, pady=10)
        
        self.lbl_estimate = ctk.CTkLabel(stats_frame, text="")
        self.lbl_estimate.pack(side="right", padx=20, pady=10)

        # === Duration Presets ===
        preset_frame = ctk.CTkFrame(main_frame)
        preset_frame.pack(fill="x", pady=(0, 8))
        
        preset_label = ctk.CTkLabel(preset_frame, text=self._tr("duration"))
        preset_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.entry_duration = ctk.CTkEntry(preset_frame, width=60)
        self.entry_duration.insert(0, "60")
        self.entry_duration.pack(side="left", padx=(0, 10), pady=10)
        self.entry_duration.bind("<KeyRelease>", self._update_estimate)
        
        # Preset buttons
        presets = [("1m", 1), ("5m", 5), ("30m", 30), ("1h", 60), ("2h", 120)]
        for label, mins in presets:
            btn = ctk.CTkButton(
                preset_frame, text=label, width=40,
                command=lambda m=mins: self._set_duration(m)
            )
            btn.pack(side="left", padx=2, pady=10)
        
        # === Settings Row 1 ===
        settings1 = ctk.CTkFrame(main_frame)
        settings1.pack(fill="x", pady=(0, 8))
        
        # Output name
        name_label = ctk.CTkLabel(settings1, text=self._tr("output_name"))
        name_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.entry_output_name = ctk.CTkEntry(settings1, width=150)
        self.entry_output_name.insert(0, "mix_output")
        self.entry_output_name.pack(side="left", padx=(0, 10), pady=10)
        
        # Format selector
        format_label = ctk.CTkLabel(settings1, text=self._tr("format"))
        format_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.format_var = ctk.StringVar(value="MP4")
        self.format_menu = ctk.CTkOptionMenu(
            settings1, values=["MP4", "MKV", "WebM"], 
            variable=self.format_var, width=80
        )
        self.format_menu.pack(side="left", padx=(0, 10), pady=10)
        
        # Save To button
        self.btn_save_to = ctk.CTkButton(
            settings1, text=self._tr("save_to"), width=100,
            command=self._select_output_folder
        )
        self.btn_save_to.pack(side="right", padx=10, pady=10)
        
        # === Settings Row 2 ===
        settings2 = ctk.CTkFrame(main_frame)
        settings2.pack(fill="x", pady=(0, 8))
        
        # Smooth Audio checkbox
        self.var_smooth_audio = ctk.BooleanVar(value=True)
        self.chk_smooth = ctk.CTkCheckBox(
            settings2, text=self._tr("smooth_audio"), variable=self.var_smooth_audio,
            command=self._update_estimate
        )
        self.chk_smooth.pack(side="left", padx=10, pady=10)
        
        # Playlist order
        order_label = ctk.CTkLabel(settings2, text=self._tr("playlist_order"))
        order_label.pack(side="left", padx=(20, 5), pady=10)
        
        self.order_var = ctk.StringVar(value="Random")
        self.order_menu = ctk.CTkOptionMenu(
            settings2, values=[self._tr("random"), self._tr("alphabetical"), self._tr("manual")],
            variable=self.order_var, width=100,
            command=self._on_order_change
        )
        self.order_menu.pack(side="left", padx=(0, 10), pady=10)

        # === Progress Bar ===
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 8))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0)
        
        self.lbl_progress = ctk.CTkLabel(progress_frame, text="")
        self.lbl_progress.pack(pady=(0, 10))
        
        # === Start Button ===
        self.btn_start = ctk.CTkButton(
            main_frame, text=self._tr("start"), height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_mixing
        )
        self.btn_start.pack(fill="x", pady=(5, 8))
        
        # === Batch Controls ===
        batch_frame = ctk.CTkFrame(main_frame)
        batch_frame.pack(fill="x", pady=(0, 8))
        
        self.btn_add_batch = ctk.CTkButton(
            batch_frame, text=self._tr("add_to_batch"), width=120,
            command=self._add_to_batch
        )
        self.btn_add_batch.pack(side="left", padx=10, pady=10)
        
        self.btn_clear_batch = ctk.CTkButton(
            batch_frame, text=self._tr("clear_batch"), width=100,
            command=self._clear_batch
        )
        self.btn_clear_batch.pack(side="left", padx=5, pady=10)
        
        self.btn_run_batch = ctk.CTkButton(
            batch_frame, text=self._tr("run_batch", 0), width=140,
            command=self._run_batch, state="disabled"
        )
        self.btn_run_batch.pack(side="right", padx=10, pady=10)
        
        # === Log Section ===
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=80)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _log(self, message):
        """Add message to log textbox."""
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
    
    def _change_language(self, choice):
        """Change UI language."""
        self.lang = "id" if choice == "Indonesia" else "en"
        self.t = TRANSLATIONS[self.lang]
        self._refresh_ui_text()
    
    def _refresh_ui_text(self):
        """Refresh all UI text after language change."""
        self.title(f"{self._tr('title')} v{VERSION}")
        self.btn_video.configure(text=self._tr("select_video"))
        self.btn_music.configure(text=self._tr("select_music"))
        self.btn_update.configure(text=self._tr("check_update"))
        self.btn_save_to.configure(text=self._tr("save_to"))
        self.chk_smooth.configure(text=self._tr("smooth_audio"))
        self.btn_start.configure(text=self._tr("start"))
        self.btn_add_batch.configure(text=self._tr("add_to_batch"))
        self.btn_clear_batch.configure(text=self._tr("clear_batch"))
        self.btn_run_batch.configure(text=self._tr("run_batch", len(self.batch_jobs)))
        self.lbl_video_count.configure(text=f"{self._tr('videos')}: {self.video_count}")
        self.lbl_music_count.configure(text=f"{self._tr('music')}: {self.music_count}")
        
        # Update order menu options
        self.order_menu.configure(values=[self._tr("random"), self._tr("alphabetical"), self._tr("manual")])

    def _on_video_drop(self, event):
        """Handle drag & drop for video folder."""
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self._set_video_folder(path)
    
    def _on_music_drop(self, event):
        """Handle drag & drop for music folder."""
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self._set_music_folder(path)
    
    def _select_video_folder(self):
        folder = filedialog.askdirectory(title="Select Video Folder")
        if folder:
            self._set_video_folder(folder)
    
    def _set_video_folder(self, folder):
        self.video_folder = folder
        self.lbl_video_path.configure(text=self._truncate_path(folder))
        videos = get_video_files(folder)
        self.video_count = len(videos)
        self.lbl_video_count.configure(text=f"{self._tr('videos')}: {self.video_count}")
        self._log(self._tr("found_videos", self.video_count))
        self._update_estimate()
    
    def _select_music_folder(self):
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self._set_music_folder(folder)
    
    def _set_music_folder(self, folder):
        self.music_folder = folder
        self.lbl_music_path.configure(text=self._truncate_path(folder))
        self.music_files = get_audio_files(folder)
        self.music_count = len(self.music_files)
        self.lbl_music_count.configure(text=f"{self._tr('music')}: {self.music_count}")
        self._log(self._tr("found_music", self.music_count))
        self._update_estimate()
    
    def _select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self._log(self._tr("output_folder", folder))
    
    def _truncate_path(self, path, max_len=40):
        """Truncate long paths for display."""
        if len(path) > max_len:
            return "..." + path[-(max_len - 3):]
        return path
    
    def _set_duration(self, minutes):
        """Set duration from preset button."""
        self.entry_duration.delete(0, "end")
        self.entry_duration.insert(0, str(minutes))
        self._update_estimate()
    
    def _update_estimate(self, event=None):
        """Update estimated processing time."""
        try:
            duration = float(self.entry_duration.get())
            smooth = self.var_smooth_audio.get()
            
            if smooth:
                # Audio crossfade: ~30 sec per hour of output
                est_seconds = (duration / 60) * 30
            else:
                # Pure copy: ~5 sec per hour
                est_seconds = (duration / 60) * 5
            
            if est_seconds < 60:
                est_str = f"~{int(est_seconds)} sec"
            else:
                est_str = f"~{int(est_seconds / 60)} min"
            
            self.lbl_estimate.configure(text=self._tr("estimated_time", est_str))
        except ValueError:
            self.lbl_estimate.configure(text="")
    
    def _on_order_change(self, choice):
        """Handle playlist order change."""
        if choice == self._tr("manual") or choice == "Manual...":
            self._show_manual_order_dialog()

    def _show_manual_order_dialog(self):
        """Show dialog to manually order music files."""
        if not self.music_files:
            messagebox.showwarning("Warning", "Please select a music folder first")
            self.order_var.set(self._tr("random"))
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manual Playlist Order")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Listbox with scrollbar
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.order_listbox = ctk.CTkTextbox(list_frame, height=350)
        self.order_listbox.pack(fill="both", expand=True)
        
        # Populate with filenames
        for f in self.music_files:
            self.order_listbox.insert("end", os.path.basename(f) + "\n")
        
        # Instructions
        instr = ctk.CTkLabel(dialog, text="Edit the order above (one file per line)")
        instr.pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        def apply_order():
            lines = self.order_listbox.get("1.0", "end").strip().split("\n")
            # Reorder music_files based on the text
            new_order = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                for f in self.music_files:
                    if os.path.basename(f) == line:
                        new_order.append(f)
                        break
            if new_order:
                self.music_files = new_order
            dialog.destroy()
        
        ctk.CTkButton(btn_frame, text="Apply", command=apply_order).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
    
    def _get_ordered_music(self):
        """Get music files in selected order."""
        order = self.order_var.get()
        files = self.music_files.copy()
        
        if order == self._tr("alphabetical") or order == "A-Z":
            files.sort(key=lambda x: os.path.basename(x).lower())
        elif order == self._tr("random") or order == "Random" or order == "Acak":
            import random
            random.shuffle(files)
        # Manual order is already applied to self.music_files
        
        return files
    
    def _check_update(self):
        """Check for updates from GitHub."""
        threading.Thread(target=self._do_check_update, args=(True,), daemon=True).start()
    
    def _check_update_silent(self):
        """Silent update check on startup."""
        self._do_check_update(show_no_update=False)
    
    def _do_check_update(self, show_no_update=True):
        """Perform update check."""
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Mixit"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest = data.get("tag_name", "").lstrip("v")
                
                if latest and latest != VERSION:
                    self.after(0, lambda: self._show_update_dialog(latest, data.get("html_url", "")))
                elif show_no_update:
                    self.after(0, lambda: messagebox.showinfo("Update", self._tr("no_update")))
        except Exception:
            if show_no_update:
                self.after(0, lambda: messagebox.showinfo("Update", self._tr("no_update")))
    
    def _show_update_dialog(self, version, url):
        """Show update available dialog."""
        if messagebox.askyesno("Update", self._tr("new_version", version)):
            webbrowser.open(url)

    def _add_to_batch(self):
        """Add current settings to batch queue."""
        if not self.video_folder:
            messagebox.showerror(self._tr("error_title"), self._tr("error_no_video"))
            return
        
        try:
            duration = float(self.entry_duration.get()) * 60
        except ValueError:
            messagebox.showerror(self._tr("error_title"), self._tr("error_duration"))
            return
        
        output_name = self.entry_output_name.get().strip() or "mix_output"
        fmt = self.format_var.get().lower()
        if not output_name.endswith(f".{fmt}"):
            output_name = output_name.rsplit(".", 1)[0] + f".{fmt}"
        
        job = {
            "video_folder": self.video_folder,
            "music_files": self._get_ordered_music() if self.music_folder else None,
            "duration": duration,
            "output_name": f"batch_{len(self.batch_jobs)+1}_{output_name}",
            "smooth_audio": self.var_smooth_audio.get(),
            "format": fmt
        }
        
        self.batch_jobs.append(job)
        self.btn_run_batch.configure(
            text=self._tr("run_batch", len(self.batch_jobs)),
            state="normal"
        )
        self._log(f"Added to batch: {job['output_name']}")
    
    def _clear_batch(self):
        """Clear batch queue."""
        self.batch_jobs = []
        self.btn_run_batch.configure(
            text=self._tr("run_batch", 0),
            state="disabled"
        )
        self._log("Batch cleared")
    
    def _run_batch(self):
        """Run all batch jobs."""
        if not self.batch_jobs:
            return
        
        if self.is_mixing:
            self._log(self._tr("already_mixing"))
            return
        
        self.is_mixing = True
        self.btn_start.configure(state="disabled")
        self.btn_run_batch.configure(state="disabled")
        
        threading.Thread(target=self._execute_batch, daemon=True).start()
    
    def _execute_batch(self):
        """Execute batch jobs in background."""
        completed = 0
        total = len(self.batch_jobs)
        
        for i, job in enumerate(self.batch_jobs):
            self.after(0, lambda j=job: self._log(f"Batch {i+1}/{total}: {j['output_name']}"))
            
            try:
                output_folder = self.output_folder or job["video_folder"]
                output_path = os.path.join(output_folder, job["output_name"])
                
                self.engine.render_concat_copy(
                    video_folder=job["video_folder"],
                    output_path=output_path,
                    target_duration=job["duration"],
                    music_files=job["music_files"],
                    smart_audio=job["smooth_audio"],
                    output_format=job["format"],
                    callback=lambda line: self._update_progress_from_line(line, job["duration"])
                )
                completed += 1
            except Exception as e:
                self.after(0, lambda e=e: self._log(f"Batch job failed: {e}"))
        
        self.after(0, lambda: self._on_batch_complete(completed))
    
    def _on_batch_complete(self, completed):
        """Called when batch is complete."""
        self.is_mixing = False
        self.btn_start.configure(state="normal")
        self.btn_run_batch.configure(state="normal" if self.batch_jobs else "disabled")
        self.progress_bar.set(0)
        self.lbl_progress.configure(text="")
        
        self._log(self._tr("batch_complete", completed))
        messagebox.showinfo(self._tr("success_title"), self._tr("batch_complete", completed))
        self._clear_batch()

    def _start_mixing(self):
        if self.is_mixing:
            self._log(self._tr("already_mixing"))
            return
        
        # Validation
        if not self.video_folder:
            messagebox.showerror(self._tr("error_title"), self._tr("error_no_video"))
            return
        
        if self.video_count == 0:
            messagebox.showerror(self._tr("error_title"), self._tr("error_no_video_files"))
            return
        
        try:
            duration_minutes = float(self.entry_duration.get())
            if duration_minutes <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(self._tr("error_title"), self._tr("error_duration"))
            return
        
        # Prepare output path
        output_name = self.entry_output_name.get().strip() or "mix_output"
        fmt = self.format_var.get().lower()
        if not output_name.endswith(f".{fmt}"):
            output_name = output_name.rsplit(".", 1)[0] + f".{fmt}"
        
        if self.output_folder:
            output_path = os.path.join(self.output_folder, output_name)
        else:
            output_path = os.path.join(self.video_folder, output_name)
        
        # Get settings
        smooth_audio = self.var_smooth_audio.get()
        target_duration = duration_minutes * 60  # Convert to seconds
        
        # Get music files in order
        music_files = self._get_ordered_music() if self.music_folder and self.music_count > 0 else None
        
        # Log mode
        if smooth_audio:
            self._log(self._tr("mode_crossfade"))
        else:
            self._log(self._tr("mode_copy"))
        
        # Start mixing in background thread
        self.is_mixing = True
        self.btn_start.configure(state="disabled", text=self._tr("mixing"))
        self.progress_bar.set(0)
        
        thread = threading.Thread(
            target=self._run_mix,
            args=(output_path, target_duration, music_files, smooth_audio, fmt),
            daemon=True
        )
        thread.start()
    
    def _run_mix(self, output_path, target_duration, music_files, smooth_audio, output_format):
        """Run mixing in background thread."""
        try:
            def progress_callback(line):
                self._update_progress_from_line(line, target_duration)
            
            self.engine.render_concat_copy(
                video_folder=self.video_folder,
                output_path=output_path,
                target_duration=target_duration,
                music_files=music_files,
                smart_audio=smooth_audio,
                output_format=output_format,
                callback=progress_callback
            )
            
            self.after(0, lambda: self._on_mix_complete(True, output_path))
            
        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda: self._on_mix_complete(False, error_msg))
    
    def _update_progress_from_line(self, line, target_duration):
        """Parse FFmpeg output and update progress bar."""
        if "time=" in line:
            try:
                # Extract time from ffmpeg output
                time_str = line.split("time=")[1].split()[0]
                parts = time_str.split(":")
                if len(parts) == 3:
                    h, m, s = parts
                    current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    progress = min(current_seconds / target_duration, 1.0)
                    
                    self.after(0, lambda p=progress: self._update_progress_ui(p))
            except (IndexError, ValueError):
                pass
    
    def _update_progress_ui(self, progress):
        """Update progress bar and label."""
        self.progress_bar.set(progress)
        self.lbl_progress.configure(text=self._tr("progress", int(progress * 100)))
    
    def _on_mix_complete(self, success, result):
        """Called when mixing is complete."""
        self.is_mixing = False
        self.btn_start.configure(state="normal", text=self._tr("start"))
        self.progress_bar.set(1.0 if success else 0)
        
        if success:
            self.lbl_progress.configure(text=self._tr("progress", 100))
            self._log(self._tr("success", result))
            messagebox.showinfo(self._tr("success_title"), f"{self._tr('success_msg')}\n\n{result}")
        else:
            self.lbl_progress.configure(text="")
            self._log(self._tr("error", result))
            messagebox.showerror(self._tr("error_title"), f"{self._tr('mix_failed')}\n{result}")


if __name__ == "__main__":
    app = MixitApp()
    app.mainloop()
