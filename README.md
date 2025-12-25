# 🎬 Mixit - Ultra Fast Video Mixer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

🌐 **Language:** English | [Bahasa Indonesia](README.id.md)

Combine videos and music into one mixed video in seconds! Perfect for video compilations, streaming backgrounds, or YouTube content.

**⚡ 1 hour video = ~5-30 seconds processing** (no rendering, low-end PC friendly!)

![Mixit Screenshot](assets/screenshot.png)

---

## 📑 Table of Contents

- [Download & Install](#-download--install)
- [Build Windows App](#-build-windows-app-exe)
- [How to Use](#-how-to-use)
- [Features](#-features)
- [Tips](#-tips)
- [Author](#-author)
- [License](#-license)

---

## 📥 Download & Install

### Option 1: Download Release (Recommended)

1. Go to [Releases](../../releases) page
2. Download `Mixit.zip` from latest release
3. Extract zip
4. Run `Mixit.exe`

> ⚠️ Make sure `bin/` folder (containing `ffmpeg.exe` & `ffprobe.exe`) is next to `Mixit.exe`

---

### Option 2: Run from Source Code

**Step 1: Download Project**
```bash
git clone https://github.com/sondero-ai/mixit.git
cd mixit
```
Or click green **Code** button → **Download ZIP** → Extract

**Step 2: Install Python**
- Download from [python.org](https://www.python.org/downloads/) (version 3.10+)
- During install, check ✅ **Add Python to PATH**

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Download FFmpeg**
- Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) (choose `ffmpeg-release-essentials.zip`)
- Extract, copy `ffmpeg.exe` and `ffprobe.exe` to `bin/` folder

**Step 5: Run**
```bash
python main.py
```

---

## 🔨 Build Windows App (.exe)

Want a standalone app without Python?

```bash
pip install pyinstaller
pyinstaller Mixit.spec
```

Output is in `dist/Mixit.exe`. Also copy `bin/` folder next to the exe.

---

## 🎯 How to Use

1. **Select video folder** - Click button or drag & drop folder
2. **Select music folder** - Click button or drag & drop folder  
3. **Set duration** - Type manually or click preset (1m, 5m, 30m, 1h, 2h)
4. **Click START MIXING** - Wait a moment, done!

### Additional Options
| Option | Function |
|--------|----------|
| **Smooth Audio** | Crossfade between songs (smoother) |
| **Playlist Order** | Music order: Random / A-Z / Manual |
| **Format** | Output: MP4 or MKV |
| **Batch Mode** | Create multiple mixes at once |

---

## ✨ Features

- ⚡ Ultra fast (stream copy, no rendering)
- 🎲 Auto shuffle videos & music
- 🔄 Auto-loop until duration reached
- 🎵 Multi-track music with crossfade
- 🎬 Last song finishes naturally
- 📁 Drag & drop support
- 🌐 English & Bahasa Indonesia
- 📦 Batch processing

---

## ⚠️ Tips

- **Same video format** = better results (e.g., all MP4 1080p)
- **Same audio format** = Fast Audio mode works (e.g., all MP3)
- **Output duration** = may be slightly longer (last song finishes first)

---

## 👤 Author

**Sondero AI**

- 🌐 Portfolio: [sondero.xyz](https://sondero.xyz)
- 📰 AI News & Tools: [cogitodaily.com](https://cogitodaily.com)
- 💻 GitHub: [@sondero-ai](https://github.com/sondero-ai)

---

## 📄 License

**Personal Use Only** - This software is free for personal, non-commercial use. Redistribution or sale is prohibited.

---

Made with ❤️ using Python & FFmpeg
