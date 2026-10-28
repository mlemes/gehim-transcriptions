"""Transcribe every audio/video file in ./input into ./output.

Uses faster-whisper (open-source Whisper models, runs offline after the first
model download). The spoken language is detected automatically and restricted
to Portuguese, English, Italian and Spanish.

For each input file "name.ext" it writes output/name.txt and output/name.srt.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio

ALLOWED = ["pt", "en", "it", "es"]
LANG_NAMES = {"pt": "Portuguese", "en": "English", "it": "Italian", "es": "Spanish"}
MEDIA_EXTS = {
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".amr",
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".mts", ".m2ts",
    ".ts", ".3gp", ".mpg", ".mpeg", ".m4v",
}
SAMPLE_RATE = 16000
WINDOW = 30 * SAMPLE_RATE


def detect_language(model, audio, samples=5):
    """Pick the most likely of ALLOWED by summing probabilities over several
    speech-bearing 30 s windows spread across the file."""
    n = len(audio)
    starts = list(range(0, max(n - WINDOW, 0) + 1, WINDOW))
    if len(starts) > samples:
        starts = [starts[i] for i in np.linspace(0, len(starts) - 1, samples).astype(int)]
    scores = dict.fromkeys(ALLOWED, 0.0)
    for s in starts:
        chunk = audio[s:s + WINDOW]
        if len(chunk) < SAMPLE_RATE or np.sqrt(np.mean(chunk ** 2)) < 0.005:
            continue  # too short or silent
        _, _, probs = model.detect_language(chunk)
        probs = dict(probs)
        for lang in ALLOWED:
            scores[lang] += probs.get(lang, 0.0)
    if not any(scores.values()):
        return None, scores
    return max(scores, key=scores.get), scores


def ts(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def transcribe_file(model, path, out_dir, forced_lang):
    audio = decode_audio(str(path), sampling_rate=SAMPLE_RATE)
    dur = len(audio) / SAMPLE_RATE
    if forced_lang:
        lang = forced_lang
    else:
        lang, scores = detect_language(model, audio)
        if lang is None:
            print("  no speech detected, skipping")
            return
    print(f"  language: {LANG_NAMES[lang]} ({lang}), duration {dur / 60:.1f} min")

    segments, _ = model.transcribe(
        audio, language=lang, vad_filter=True, beam_size=5,
        condition_on_previous_text=False,
    )
    txt_lines, srt_lines = [], []
    for i, seg in enumerate(segments, 1):
        text = seg.text.strip()
        txt_lines.append(text)
        srt_lines.append(f"{i}\n{ts(seg.start)} --> {ts(seg.end)}\n{text}\n")
        print(f"\r  {seg.end / dur:6.1%}", end="", flush=True)
    print()

    (out_dir / f"{path.stem}.txt").write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    (out_dir / f"{path.stem}.srt").write_text("\n".join(srt_lines), encoding="utf-8")


def main():
    root = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=root / "input")
    ap.add_argument("--output", type=Path, default=root / "output")
    ap.add_argument("--model", default="large-v3-turbo",
                    help="Whisper model: tiny, base, small, medium, large-v3, large-v3-turbo (default)")
    ap.add_argument("--device", default="auto", help="auto, cpu or cuda")
    ap.add_argument("--language", choices=ALLOWED, help="skip detection and force a language")
    ap.add_argument("--overwrite", action="store_true", help="redo files that already have output")
    args = ap.parse_args()

    files = sorted(p for p in args.input.iterdir() if p.suffix.lower() in MEDIA_EXTS)
    args.output.mkdir(exist_ok=True)
    todo = [p for p in files if args.overwrite or not (args.output / f"{p.stem}.txt").exists()]
    if not files:
        sys.exit(f"No audio/video files found in {args.input}")
    print(f"{len(files)} file(s) found, {len(todo)} to process")
    if not todo:
        return

    device = args.device
    compute = "float16" if device == "cuda" else "int8"
    print(f"Loading model '{args.model}' (first run downloads it)...")
    model = WhisperModel(args.model, device=device, compute_type=compute,
                         download_root=str(root / "models"))

    for n, path in enumerate(todo, 1):
        print(f"[{n}/{len(todo)}] {path.name}")
        t0 = time.time()
        try:
            transcribe_file(model, path, args.output, args.language)
        except Exception as e:  # keep going with the remaining files
            print(f"  FAILED: {e}")
            continue
        print(f"  done in {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
