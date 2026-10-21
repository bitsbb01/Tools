# JGJG Video Studio

JGJG Video Studio is a free, Windows-first desktop video editor. Editing runs locally with FFmpeg; video files are not uploaded to a server.

## First release

- Trim a video by start time and clip length.
- Fit the video to common landscape, square, or vertical output sizes without cropping.
- Optionally replace the source audio with a selected music track.
- Export an MP4 with H.264 video and AAC audio.
- Cancel an export in progress.
- Optionally download the Wan2.2 TI2V-5B local model from inside the app.

## Use the Windows app

Download **JGJG-Video-Studio-Setup.exe** from the latest successful Windows build or GitHub release and run the installer. It installs a normal Windows app with a Start menu shortcut; a desktop shortcut is optional. The installer includes the app and FFmpeg, so users do not need Python, FFmpeg, or command-line steps.

FFmpeg is included as a separate LGPL shared component. The installer shows its license and installs third-party notices with the app.

## Optional local AI model

The app includes an **Install AI model** button. It downloads the Wan2.2 TI2V-5B model from its official Hugging Face repository into the user's local app data folder. The download is about 34.2 GB, and the app recommends 38 GB free disk space. Pausing keeps completed files so the user can resume later.

The model's repository is labeled Apache 2.0. The app opens the model page before downloading. The model can require substantial GPU memory; the Wan project lists 24 GB of VRAM for the 720p example. Installing model files alone does not yet enable video generation; the local generation engine and generation controls are still being integrated.

See the [official Wan2.2 project](https://github.com/Wan-Video/Wan2.2) and [model files and license](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B).

## Run from source

1. Install Python 3.10 or newer.
2. For source runs, install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and make sure `ffmpeg` is on PATH.
3. Run `python main.py`.

No Python packages are needed to run the editor itself. Run `python -m unittest discover -s tests` to run the command-builder tests.

## Build the Windows installer

The GitHub Actions workflow tests the app, downloads and checksum-verifies the FFmpeg LGPL shared build, creates a standalone executable, and packages it with Inno Setup. Users installing the release do not need Python or a separate FFmpeg install.

## Privacy and safety

- Editing and model inference are designed to run on the user's computer.
- The app does not upload source video files.
- The app never deletes or overwrites the source video.
- The user selects the output path; exports use a new MP4 file.
- The model download connects to Hugging Face to retrieve the model files.

## License

App source: MIT License. FFmpeg and any AI model are separate components governed by their own licenses. See [third-party notices](THIRD-PARTY-NOTICES.md).
