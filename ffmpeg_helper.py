import os
import sys
import shutil

def get_base_path():
    """
    Returns the base path for the application.
    Works correctly for both normal Python execution and PyInstaller bundles.
    """
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path():
    """
    Returns the path to ffmpeg.exe.
    Priority:
      1. Bundled in 'bin' folder next to the executable/script.
      2. System PATH.
    """
    base = get_base_path()
    bundled = os.path.join(base, 'bin', 'ffmpeg.exe')
    
    if os.path.exists(bundled):
        return bundled
    
    # Fallback to system PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg
    
    raise FileNotFoundError("FFmpeg not found. Place ffmpeg.exe in the 'bin' folder or install it to PATH.")

def get_ffprobe_path():
    """
    Returns the path to ffprobe.exe.
    Priority:
      1. Bundled in 'bin' folder next to the executable/script.
      2. System PATH.
    """
    base = get_base_path()
    bundled = os.path.join(base, 'bin', 'ffprobe.exe')
    
    if os.path.exists(bundled):
        return bundled
    
    # Fallback to system PATH
    system_ffprobe = shutil.which('ffprobe')
    if system_ffprobe:
        return system_ffprobe
    
    raise FileNotFoundError("FFprobe not found. Place ffprobe.exe in the 'bin' folder or install it to PATH.")
