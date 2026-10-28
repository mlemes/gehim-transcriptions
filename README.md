# Transcription

Turns speech in video and audio files into text. Portuguese, English, Italian and Spanish are recognised automatically.

## How to use (Windows)

1. Put your video or audio files in the **`input`** folder.
2. Double-click **`run.bat`**.
3. Wait. Your transcriptions appear in the **`output`** folder: a `.txt` file (plain text) and a `.srt` file (subtitles with times) for each input file.

The first time, it installs what it needs by itself (Python and some libraries) and downloads the speech model (about 1.6 GB). This needs an internet connection and takes several minutes. After that it works offline.

Notes:
- Long files take a while. A computer without a graphics card transcribes roughly in real time or slower.
- Files that already have a transcription in `output` are skipped. Delete the `.txt` to redo one.
- Supported: mp4, mkv, mov, avi, mts, webm, mp3, wav, m4a, flac, ogg and more.

## For developers

Engine: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with OpenAI's open-source Whisper `large-v3-turbo`. No ffmpeg needed (audio is decoded with PyAV). The model is stored in `models/`.
Language detection samples several 30-second windows and picks the best of the four supported languages.

`run.bat` passes options through to `transcribe.py`: `--model small` (faster, less accurate), `--language pt|en|it|es` (skip detection), `--device cuda`, `--overwrite`.
