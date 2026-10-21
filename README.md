# JGJG Video Studio

JGJG Video Studio is a free, Windows-first desktop video editor. The first version performs local edits with FFmpeg and does not upload video files to a server.

## First release

- Trim a video by start time and clip length.
- Fit the video to common landscape, square, or vertical output sizes without cropping.
- Optionally replace the source audio with a selected music track.
- Export an MP4 with H.264 video and AAC audio.
- Cancel an export in progress.

## Use the Windows app

Download **JGJG Video Studio.exe** from the latest successful Windows build or GitHub release, then double-click it. It is packaged as a standalone Windows executable, so users do not need to install Python or run Python commands.

The current build does require FFmpeg to be installed on the computer and available on PATH. The app's **Get FFmpeg** button opens the download instructions. A future installer can bundle FFmpeg so users can install both together; FFmpeg's separate license and corresponding source notices need to be included with that distribution.

## Optional local AI generation

Local AI generation is planned as an optional install. The small editor download should stay usable without AI; users who want generation can opt in to downloading a compatible model pack. This avoids making every app download tens of gigabytes. The model will run on the user's computer, and generation speed and availability depend on the user's GPU, memory, and free disk space.

One candidate is Wan2.2 TI2V-5B, which supports text-to-video and image-to-video. Its official model repository is about 34 GB, and the Wan project documents 720p output and a consumer GPU example (RTX 4090). Model weights and code have separate licenses; the chosen version's terms will be shown before download. See the [official Wan2.2 project](https://github.com/Wan-Video/Wan2.2) and [model files and license](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B).

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

The executable currently expects FFmpeg to be installed separately. AI weights will be installed as an optional model pack rather than bundled into the small editor executable.

## Privacy and safety

- The app processes the selected files on the user's computer.
- It never deletes or overwrites the source video.
- The user selects the output path; exports use a new MP4 file.
- The first release does not include an AI model or contact a generation service.

## License

App source: MIT License. FFmpeg and any future AI model are separate components governed by their own licenses.
