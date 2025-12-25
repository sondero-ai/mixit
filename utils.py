import os
import subprocess
from ffmpeg_helper import get_ffprobe_path

def get_media_duration(file_path):
    """
    Get duration of a media file using ffprobe.
    Returns float seconds.
    """
    try:
        ffprobe = get_ffprobe_path()
        cmd = [
            ffprobe, 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        output = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8').strip()
        return float(output)
    except Exception as e:
        print(f"Error probing {file_path}: {e}")
        return 0.0

def scan_folder(folder_path, extensions):
    """
    Scan folder for files with specific extensions.
    """
    files = []
    if not os.path.isdir(folder_path):
        return files
        
    for f in os.listdir(folder_path):
        if any(f.lower().endswith(ext) for ext in extensions):
            full_path = os.path.join(folder_path, f)
            files.append(full_path)
    return files

def get_video_files(folder_path):
    return scan_folder(folder_path, ['.mp4', '.mov', '.avi', '.mkv'])

def get_audio_files(folder_path):
    return scan_folder(folder_path, ['.mp3', '.wav', '.aac', '.m4a'])
