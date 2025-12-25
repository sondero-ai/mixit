# Changelog

All notable changes to Mixit will be documented in this file.

## [1.1.0] - 2024-12-26

### Added
- **Drag & Drop Support** - Drag folders directly onto the app
- **Progress Bar** - Visual progress indicator with percentage
- **Duration Presets** - Quick buttons: 1m, 5m, 30m, 1h, 2h
- **Estimated Time** - Shows estimated processing time before mixing
- **Output Format Selection** - Choose between MP4, MKV formats
- **Multi-language Support** - English and Indonesian (Bahasa Indonesia)
- **Update Checker** - Automatic check for new versions from GitHub
- **Batch Processing** - Queue multiple mix jobs and run them all at once
- **Playlist Order Options** - Random, Alphabetical (A-Z), or Manual ordering
- **Manual Playlist Editor** - Drag to reorder songs manually
- **Auto FFmpeg Detection** - Guides user to download FFmpeg if not found

### Changed
- Simplified to Copy Mode only (no video re-encoding) for maximum speed
- Audio crossfade is now the only rendering option (fast on any PC)
- Improved temp file handling
- Better error messages

### Removed
- Full Render mode (video transitions) - removed to keep app fast and simple
- Resolution presets - not needed for copy mode

## [1.0.1] - 2024-12-26

### Fixed
- Removed duplicate codec arguments in `mixer_engine.py`
- Removed unused imports in `utils.py` and `mixer_engine.py`
- Temp files now created in system temp folder

## [1.0.0] - Initial Release

### Features
- Ultra fast video mixing using FFmpeg stream copy
- Random video and music shuffling
- Auto-loop for videos and music
- Multi-track audio playlist support
- Natural ending (last song finishes completely)
- Modern dark mode UI
