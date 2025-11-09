"""
Multi-site Video/Audio Downloader — Python 3.13 safe version
Author: Mohammad Imran Ali
Email: nsbathorce@gmail.com
LinkedIn: https://www.linkedin.com/in/mohammad-imran-ali-90772530/

Requirements:
- Python 3.11+ (Python 3.13 tested)
- ffmpeg installed
- Install packages:
    py -m pip install yt-dlp customtkinter pillow
"""

import os
import threading
import webbrowser
from tkinter import filedialog, messagebox, simpledialog

try:
    import customtkinter as ctk
except Exception:
    raise SystemExit("Missing dependency: customtkinter. Install: py -m pip install customtkinter")

try:
    from yt_dlp import YoutubeDL
except Exception:
    raise SystemExit("Missing dependency: yt-dlp. Install: py -m pip install yt-dlp")

from customtkinter import CTkImage
from PIL import Image

# ---------------------------
# Configuration
# ---------------------------
SPLASH_SECONDS = 3
APP_WIDTH = 760
APP_HEIGHT = 460
SPLASH_WIDTH = 500
SPLASH_HEIGHT = 350

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
if not os.path.isfile(FFMPEG_PATH):
    raise FileNotFoundError(f"FFmpeg not found at {FFMPEG_PATH}. Please check path.")

progress_state = {
    "percent": 0.0,
    "status": "",
    "filename": "",
    "active": False,
}

# Global references for logging
root_ref = None
log_widget_ref = None

# ---------------------------
# Thread-safe GUI call
# ---------------------------
def safe_gui_call(root, func, *args, **kwargs):
    root.after(0, lambda: func(*args, **kwargs))

def write_log_safe(widget, text):
    widget.configure(state="normal")
    widget.insert("end", text)
    widget.see("end")
    widget.configure(state="disabled")

# ---------------------------
# Progress hook
# ---------------------------
def make_progress_hook():
    def hook(d):
        status = d.get("status")
        filename = os.path.basename(d.get("filename") or "")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            pct = float(downloaded)/float(total)*100 if total else 0
            progress_state.update({
                "percent": pct,
                "status": "Downloading",
                "filename": filename,
                "active": True
            })
        elif status == "finished":
            progress_state.update({
                "percent": 100.0,
                "status": "Finished",
                "filename": filename,
                "active": True
            })
            # Append downloaded filename to log
            if root_ref and log_widget_ref:
                safe_gui_call(root_ref, write_log_safe, log_widget_ref, f"Downloaded: {filename}\n")
        elif status == "error":
            progress_state.update({"status": "Error", "active": False})
    return hook

# ---------------------------
# Download logic
# ---------------------------
def run_download(root, url, out_dir, is_audio, quality_choice, file_name, video_format,
                 log_widget, btn_video, btn_audio, quality_dd, format_dd):
    safe_gui_call(root, btn_video.configure, state="disabled")
    safe_gui_call(root, btn_audio.configure, state="disabled")
    safe_gui_call(root, quality_dd.configure, state="disabled")
    safe_gui_call(root, format_dd.configure, state="disabled")

    write_log_safe(log_widget, f"Starting download: {url}\n\n")
    progress_state.update({"percent":0.0, "status":"Starting...", "filename":"", "active":True})

    # Determine format
    if is_audio:
        fmt = "bestaudio/best"
    else:
        if quality_choice == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality_choice}]+bestaudio/best[height<={quality_choice}]"

    # Output template
    outtmpl = os.path.join(out_dir, f"{file_name}.%(ext)s") if file_name else os.path.join(out_dir, "%(title).100s - %(id)s.%(ext)s")

    ydl_opts = {
        "format": fmt,
        "outtmpl": outtmpl,
        "noplaylist": False,
        "progress_hooks": [make_progress_hook()],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "retries": 3,
        "ffmpeg_location": FFMPEG_PATH,
    }

    if not is_audio:
        if video_format == "MP4":
            ydl_opts["merge_output_format"] = "mp4"
        else:
            ydl_opts["merge_output_format"] = None  # keep original container (WebM etc.)

    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }]
        ydl_opts["addmetadata"] = True

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        write_log_safe(log_widget, "\nDownload finished.\n")
    except Exception as e:
        write_log_safe(log_widget, f"\nError: {e}\n")
        if not is_audio:
            write_log_safe(log_widget, "Trying fallback format...\n")
            ydl_opts["merge_output_format"] = None
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e2:
                write_log_safe(log_widget, f"\nFallback error: {e2}\n")
    finally:
        progress_state["active"] = False
        safe_gui_call(root, btn_video.configure, state="normal")
        safe_gui_call(root, btn_audio.configure, state="normal")
        safe_gui_call(root, quality_dd.configure, state="normal")
        safe_gui_call(root, format_dd.configure, state="normal")

# ---------------------------
# Start download thread
# ---------------------------
def start_download_thread(root, url_entry, log_widget, quality_dd, format_dd, is_audio, btn_video, btn_audio):
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please paste a URL.")
        return
    out_dir = filedialog.askdirectory(title="Choose download folder")
    if not out_dir:
        return
    quality_choice = quality_dd.get()
    video_format = format_dd.get()
    file_name = simpledialog.askstring("File name", "Enter file name (without extension):")
    if not file_name:
        file_name = None
    threading.Thread(
        target=run_download,
        args=(root, url, out_dir, is_audio, quality_choice, file_name, video_format, log_widget, btn_video, btn_audio, quality_dd, format_dd),
        daemon=True
    ).start()

# ---------------------------
# Build UI
# ---------------------------
def build_ui(root):
    global root_ref, log_widget_ref
    root_ref = root

    root.title("Multi-site Video/Audio Downloader")
    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    root.minsize(700, 460)

    top_frame = ctk.CTkFrame(root, corner_radius=8)
    top_frame.pack(fill="x", padx=16, pady=(16,8))

    # Configure grid weights to fit window
    top_frame.grid_columnconfigure(0, weight=4)
    top_frame.grid_columnconfigure(1, weight=1)
    top_frame.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(top_frame, text="Paste a video URL (YouTube, TikTok, Instagram, Vimeo, ...)", anchor="w")\
        .grid(row=0, column=0, padx=10, pady=(12,6), sticky="w")
    url_entry = ctk.CTkEntry(top_frame, width=520)
    url_entry.grid(row=1, column=0, padx=10, pady=(0,12), sticky="we")

    # Quality dropdown
    ctk.CTkLabel(top_frame, text="Quality:").grid(row=0, column=1, padx=8, pady=(12,6), sticky="w")
    quality_dd = ctk.CTkOptionMenu(top_frame, values=["best","1080","720","480","360","240"])
    quality_dd.set("best")
    quality_dd.grid(row=1, column=1, padx=8, pady=(0,12), sticky="w")

    # Format dropdown
    ctk.CTkLabel(top_frame, text="Format:").grid(row=0, column=2, padx=8, pady=(12,6), sticky="w")
    format_dd = ctk.CTkOptionMenu(top_frame, values=["WebM","MP4"])
    format_dd.set("WebM")
    format_dd.grid(row=1, column=2, padx=8, pady=(0,12), sticky="w")

    # Buttons
    btn_frame = ctk.CTkFrame(root)
    btn_frame.pack(fill="x", padx=16, pady=(0,10))
    btn_video = ctk.CTkButton(btn_frame, text="Download Video", width=200,
        command=lambda: start_download_thread(root, url_entry, log_widget_ref, quality_dd, format_dd, False, btn_video, btn_audio))
    btn_video.grid(row=0, column=0, padx=(10,6), pady=8)
    btn_audio = ctk.CTkButton(btn_frame, text="Download Audio", width=200,
        command=lambda: start_download_thread(root, url_entry, log_widget_ref, quality_dd, format_dd, True, btn_video, btn_audio))
    btn_audio.grid(row=0, column=1, padx=(6,10), pady=8)

    # Progress bar
    progress_frame = ctk.CTkFrame(root)
    progress_frame.pack(fill="x", padx=16, pady=(0,10))
    progress = ctk.CTkProgressBar(progress_frame, width=APP_WIDTH-80, mode="determinate")
    progress.set(0)
    progress.pack(padx=12, pady=(10,6))
    status_label = ctk.CTkLabel(progress_frame, text="Idle")
    status_label.pack(anchor="w", padx=12, pady=(0,6))
    info_label = ctk.CTkLabel(progress_frame, text="")
    info_label.pack(anchor="w", padx=12, pady=(0,10))

    # Log textbox
    log_widget = ctk.CTkTextbox(root, width=APP_WIDTH-40, height=140)
    log_widget.pack(padx=16, pady=(0,8), fill="both", expand=True)
    write_log_safe(log_widget, "Ready. Paste a URL and click Download.\n")
    log_widget_ref = log_widget

    # Footer
    footer_frame = ctk.CTkFrame(root, height=36, corner_radius=6)
    footer_frame.pack(fill="x", side="bottom", padx=10, pady=(0,10))
    ctk.CTkLabel(footer_frame, text="© 2025 • Developed by Mohammad Imran Ali", anchor="w", fg_color="transparent")\
        .grid(row=0, column=0, padx=(8,6), pady=6, sticky="w")
    ctk.CTkButton(footer_frame, text="LinkedIn", width=100,
                   command=lambda:webbrowser.open_new("https://www.linkedin.com/in/mohammad-imran-ali-90772530/"))\
        .grid(row=0, column=1, padx=(6,8), pady=6, sticky="e")

    # Update progress
    def ui_updater():
        pct = progress_state.get("percent",0.0) or 0.0
        progress.set(pct/100.0)
        if progress_state.get("active"):
            st = progress_state.get("status","")
            fn = progress_state.get("filename","")
            status_label.configure(text=f"{st} — {fn}" if fn else st)
            info_label.configure(text=f"{pct:.1f}%")
        else:
            if pct >= 100.0:
                status_label.configure(text="Finished")
                info_label.configure(text="100%")
            else:
                status_label.configure(text="Idle")
                info_label.configure(text="")
        root.after(300, ui_updater)

    root.after(300, ui_updater)
    return root, url_entry, log_widget, btn_video, btn_audio, quality_dd, format_dd

# ---------------------------
# Splash screen
# ---------------------------
def show_splash_then_start():
    root = ctk.CTk()
    root.withdraw()
    splash = ctk.CTkToplevel(root)
    splash.overrideredirect(True)
    splash.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}+{int((splash.winfo_screenwidth()-SPLASH_WIDTH)/2)}+{int((splash.winfo_screenheight()-SPLASH_HEIGHT)/2)}")
    frame = ctk.CTkFrame(splash, corner_radius=12)
    frame.pack(fill="both", expand=True, padx=12, pady=12)

    # Load image
    image_path = os.path.join(os.path.dirname(__file__), "my_photo.jpg")
    if os.path.isfile(image_path):
        photo = CTkImage(Image.open(image_path), size=(150,150))
        ctk.CTkLabel(frame, image=photo, text="").pack(pady=(10,10))

    # Existing splash text
    ctk.CTkLabel(frame, text="Designed & Developed by", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,6))
    ctk.CTkLabel(frame, text="Mohammad Imran Ali", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0,6))
    ctk.CTkLabel(frame, text="Email: nsbathorce@gmail.com").pack(pady=(0,6))
    ctk.CTkButton(frame, text="Open LinkedIn Profile",
                   command=lambda:webbrowser.open_new("https://www.linkedin.com/in/mohammad-imran-ali-90772530/"), width=220).pack(pady=(6,14))

    def show_main():
        splash.destroy()
        root.deiconify()
    root.after(SPLASH_SECONDS*1000, show_main)
    root, url_entry, log_widget, btn_video, btn_audio, quality_dd, format_dd = build_ui(root)
    return root

# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    app_root = show_splash_then_start()
    app_root.mainloop()
