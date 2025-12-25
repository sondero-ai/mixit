"""
Mixit Mixer Engine
Core video/audio processing using FFmpeg (Copy Mode Only)
"""

import os
import random
import subprocess
import tempfile
from utils import get_media_duration
from ffmpeg_helper import get_ffmpeg_path


class MixerEngine:
    def __init__(self):
        self.crossfade_duration = 3.0  # seconds for audio crossfade

    def render_concat_copy(self, video_folder, output_path, target_duration, 
                           music_files=None, smart_audio=False, output_format="mp4", callback=None):
        """
        Ultra Fast Video Mix using stream copy (no re-encoding).
        
        Args:
            video_folder: Path to folder containing video files
            output_path: Output file path
            target_duration: Target duration in seconds
            music_files: List of music file paths (optional)
            smart_audio: If True, apply crossfade between songs (slower)
            output_format: Output format (mp4, mkv, webm)
            callback: Progress callback function
        """
        # --- VIDEO PREP ---
        video_candidates = [
            os.path.join(video_folder, f) for f in os.listdir(video_folder) 
            if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
        ]
        
        if not video_candidates:
            raise ValueError("No video files found.")

        # Shuffle Video
        pool = video_candidates.copy()
        random.shuffle(pool)
        
        # Build video list for concat (enough to cover duration)
        concat_entries = []
        total_video_duration = 0
        
        while total_video_duration < target_duration + 60:  # Buffer
            for clip in pool:
                concat_entries.append(clip)
                total_video_duration += get_media_duration(clip)
                if total_video_duration >= target_duration + 60:
                    break
            if total_video_duration < target_duration:
                random.shuffle(pool)  # Reshuffle for variety when looping
        
        # Write concat list to temp directory
        temp_dir = tempfile.gettempdir()
        list_file = os.path.join(temp_dir, "mixit_concat_list.txt")
        with open(list_file, 'w', encoding='utf-8') as f:
            for clip in concat_entries:
                safe_path = clip.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")

        # --- BUILD COMMAND ---
        cmd = [get_ffmpeg_path(), '-y']
        
        # Input 0: Video Concat
        cmd.extend(['-f', 'concat', '-safe', '0', '-i', list_file])
        
        # Audio handling
        audio_list_file = None
        
        if music_files and len(music_files) > 0:
            if smart_audio and len(music_files) > 1:
                # --- SMART MODE: Crossfade between songs (AAC encode) ---
                selected_music, audio_list_file = self._prepare_audio_crossfade(
                    music_files, target_duration, temp_dir
                )
                
                if len(selected_music) > 1:
                    # Build crossfade filter
                    filter_parts = []
                    last_label = "[1:a]"
                    
                    for i in range(1, len(selected_music)):
                        next_idx = i + 1
                        next_label = f"[{next_idx}:a]"
                        out_label = f"[a{i}]"
                        filter_parts.append(
                            f"{last_label}{next_label}acrossfade=d={self.crossfade_duration}:c1=tri:c2=tri{out_label}"
                        )
                        last_label = out_label
                    
                    # Add all audio inputs
                    for track in selected_music:
                        cmd.extend(['-i', track])
                    
                    # Add filter and mapping
                    cmd.extend(['-filter_complex', ';'.join(filter_parts)])
                    cmd.extend(['-map', '0:v', '-map', last_label])
                    cmd.extend(['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k'])
                else:
                    # Single file, still encode for consistency
                    cmd.extend(['-i', selected_music[0]])
                    cmd.extend(['-map', '0:v', '-map', '1:a'])
                    cmd.extend(['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k'])
            else:
                # --- FAST MODE: Concat audio (stream copy) ---
                selected_music = self._select_music_for_duration(music_files, target_duration)
                
                # Write audio concat list
                audio_list_file = os.path.join(temp_dir, "mixit_audio_concat_list.txt")
                with open(audio_list_file, 'w', encoding='utf-8') as f:
                    for track in selected_music:
                        safe_path = track.replace('\\', '/')
                        f.write(f"file '{safe_path}'\n")
                
                # Add audio concat input
                cmd.extend(['-f', 'concat', '-safe', '0', '-i', audio_list_file])
                cmd.extend(['-map', '0:v', '-map', '1:a', '-c', 'copy'])
        else:
            # No music - keep original video audio if exists
            cmd.extend(['-map', '0:v', '-map', '0:a?', '-c', 'copy'])
            cmd.extend(['-t', str(target_duration)])
        
        # Add shortest flag when we have music (music controls duration)
        if music_files:
            cmd.extend(['-shortest'])
        
        # Output format specific settings
        if output_format == "webm":
            # WebM needs re-encoding, but user wants copy mode
            # Fall back to mkv container which supports more codecs
            output_path = output_path.rsplit('.', 1)[0] + '.mkv'
        
        cmd.append(output_path)
        
        # Execute
        print("Running:", " ".join(cmd))
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        while True:
            line = process.stderr.readline()
            if not line:
                break
            if callback:
                callback(line)
        
        process.wait()
        
        # Cleanup temp files
        self._cleanup_temp_files(list_file, audio_list_file, temp_dir)
        
        if process.returncode != 0:
            raise Exception("Mix failed. Ensure all audio files have the same codec (e.g., all MP3).")
        
        return output_path

    def _select_music_for_duration(self, music_files, target_duration):
        """
        Select music files to fill target duration.
        Last song plays completely (natural ending).
        """
        selected = []
        current_duration = 0
        pool = music_files.copy()
        
        while current_duration < target_duration:
            if not pool:
                pool = music_files.copy()
                random.shuffle(pool)
            
            track = pool.pop(0)
            dur = get_media_duration(track)
            if dur > 0:
                selected.append(track)
                current_duration += dur
        
        return selected
    
    def _prepare_audio_crossfade(self, music_files, target_duration, temp_dir):
        """
        Prepare audio files for crossfade mixing.
        Returns list of selected tracks.
        """
        selected = []
        current_duration = 0
        pool = music_files.copy()
        
        # Account for crossfade overlap
        effective_duration = target_duration + (self.crossfade_duration * 2)
        
        while current_duration < effective_duration:
            if not pool:
                pool = music_files.copy()
                random.shuffle(pool)
            
            track = pool.pop(0)
            dur = get_media_duration(track)
            if dur > self.crossfade_duration + 1:  # Must be longer than crossfade
                selected.append(track)
                # Effective duration accounts for overlap
                if len(selected) == 1:
                    current_duration += dur
                else:
                    current_duration += (dur - self.crossfade_duration)
        
        return selected, None
    
    def _cleanup_temp_files(self, video_list, audio_list, temp_dir):
        """Clean up temporary files."""
        try:
            if video_list and os.path.exists(video_list):
                os.remove(video_list)
            if audio_list and os.path.exists(audio_list):
                os.remove(audio_list)
        except Exception:
            pass  # Ignore cleanup errors
