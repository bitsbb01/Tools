# JGJG Video Studio

JGJG Video Studio is a free, Windows-first desktop video editor. The first version performs local edits with FFmpeg and does not upload video files to a server.

## First release

- Trim a video by start time and clip length.
- Fit the video to common landscape, square, or vertical output sizes without cropping.
- Optionally replace the source audio with a selected music track.
- Export an MP4 with H.264 video and AAC audio.
- Cancel an export in progress.

AI generation is planned as an optional local engine after the editing workflow is validated. AI models will be downloaded separately because they are large and each model has its own license and hardware requirements.

## Run from source

1. Install Python 3.10 or newer.
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and make sure `ffmpeg` is on PATH. The app includes a **Get FFmpeg** shortcut to this page.
3. Run `python main.py`.

No Python packages are needed to run the editor itself. Run `python -m unittest discover -s tests` to run the command-builder tests.

## Build the Windows executable

On Windows, run:

```powershell
python -m pip install -r requirements.txt
pyinstaller --onefile --windowed --name "JGJG Video Studio" main.py
```

The executable currently expects FFmpeg to be installed separately. This keeps FFmpeg's separate license and distribution terms clear.

## Privacy and safety

- The app processes the selected files on the user's computer.
- It never deletes or overwrites the source video.
- The user selects the output path; exports use a new MP4 file.
- The first release does not include an AI model or contact a generation service.

## License

App source: MIT License. FFmpeg and any future AI model are separate components governed by their own licenses.
