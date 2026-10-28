# Transcription

Turns speech in video and audio files into text. Portuguese, English, Italian and Spanish are recognised automatically. Everything runs on your own computer: your files are never uploaded anywhere.

This tool was developed to be used by the [GEHIM group](https://historiaibericamoderna.wordpress.com/).

## What you need

- A Windows 10 or 11 computer.
- An internet connection **the first time only** (to install the tools and download the speech model, about 1.6 GB plus about 1 GB of libraries).
- About 5 GB of free disk space.
- At least 6 GB of RAM is recommended.

## Setup (one time)

1. **Get the project.** On the GitHub page, click the green **Code** button, then **Download ZIP**. Right-click the downloaded ZIP and choose **Extract All**. Put the extracted folder somewhere easy, such as `Documents`. (If you use git, `git clone` works too.)
2. **Open the extracted folder.** You should see `run.bat`, `transcribe.py` and the folders `input` and `output`.
3. That's it. The first time you run the program (next section) it installs everything else by itself: Python, the libraries and the speech model. This takes roughly 10 to 20 minutes depending on your connection.

## How to run

1. Copy the video or audio files you want transcribed into the **`input`** folder.
2. Double-click **`run.bat`**.
   - If Windows shows "Windows protected your PC", click **More info**, then **Run anyway**.
   - If Windows asks whether to allow Python to be installed, accept.
   - A black window opens and shows progress. Leave it open.
3. When the window says **Finished**, press any key to close it.
4. Open the **`output`** folder. For each file you will find:
   - `name.txt`: the plain text of the speech.
   - `name.srt`: the same text as subtitles with time stamps (works with video players such as VLC).

To transcribe more files later, put them in `input` and double-click `run.bat` again. Files that already have a result in `output` are skipped; delete their `.txt` file if you want to redo one.

### How long does it take?

On a computer without a dedicated graphics card, expect roughly the same time as the length of the recording, or longer (a 30-minute video can take 30 to 90 minutes). The window shows a percentage for the current file. You can keep using the computer, but it may be slower.

## Supported files

Video: mp4, mkv, mov, avi, webm, mts, m2ts, ts, wmv, flv, 3gp, mpg, mpeg, m4v.
Audio: mp3, wav, m4a, aac, flac, ogg, opus, wma, amr.

## Troubleshooting

| Problem | What to do |
|---|---|
| "No audio/video files found" | Put your files directly in the `input` folder (not in a sub-folder). |
| "Could not install Python automatically" | Install Python from https://www.python.org/downloads/ (tick **Add python.exe to PATH**), then double-click `run.bat` again. |
| "Setup failed" | Check your internet connection and double-click `run.bat` again. |
| The wrong language was chosen | See "Options" below to force the language. |
| A file shows `FAILED` | The file may be damaged or have no audio. The other files still finish. |
| Computer runs out of memory or is too slow | Use the smaller model (see "Options"). |

## Options (optional)

Open a terminal in the project folder and run `run.bat` with extra settings:

```
run.bat --language pt
run.bat --model small
run.bat --overwrite
```

- `--language pt` (or `en`, `it`, `es`): skip automatic detection and force a language.
- `--model small`: a faster, lighter model that is less accurate. Others: `tiny`, `base`, `medium`, `large-v3`.
- `--overwrite`: redo files that already have a result.
- `--device cuda`: use an NVIDIA graphics card, if you have one.

## For developers

Engine: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with OpenAI's open-source Whisper `large-v3-turbo`. No ffmpeg needed (audio is decoded with PyAV). The model is stored in `models/`. Language detection samples up to five 30-second windows across each file and picks the best of the four supported languages.

Manual setup:

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python transcribe.py
```
