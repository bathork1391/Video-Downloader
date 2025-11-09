📥 Multi-Site Video/Audio Downloader

A simple, efficient, and user-friendly desktop application for downloading video and audio from multiple platforms including YouTube, TikTok, Instagram, Vimeo, Facebook, and many more.

This tool allows users to choose preferred video quality and output format, and download either full videos or audio-only files with ease.

🖼️ Application Preview

(Insert your screenshot here – e.g.:)


🚀 Features

✅ Download videos from multiple platforms
✅ Choose video quality (best, 1080p, 720p, 480p, etc.)
✅ Choose video format (WebM, MP4, etc.)
✅ Download audio-only (e.g., MP3, M4A, OPUS)
✅ Simple and clean GUI – easy for all users
✅ Built-in splash screen with branding
✅ Supports YouTube, TikTok, Instagram, Vimeo, Facebook, Twitter (X) & more
✅ Progress bar & status messages
✅ Error handling and user guidance

🧑‍💻 Tech Stack
Component	Technology Used
Language	Python
GUI	Tkinter
Video Engine	yt-dlp
Media Processor	FFmpeg
📦 Installation & Usage
🔹 Option 1: Download the Executable (Recommended for Users)

Visit the Releases section and download the latest .exe file:
👉 (Link to releases will be added by you)

No installation required — just run the executable!

🔹 Option 2: Run from Source (For Developers)
Prerequisites

Ensure you have:

Python 3.8 or above

FFmpeg (added to PATH or available in project folder)

Install Dependencies:
pip install yt-dlp
pip install tkinter

Run the Application:
python downloader.py

🔧 Building a Stand-Alone EXE (Developer Guide)

To generate a Windows executable:

pyinstaller --onefile --noconsole --add-binary "ffmpeg.exe;." --add-data "my_photo.jpg;." downloader.py


The .exe will be created inside the /dist folder.

🧠 How It Works

This application internally uses:

yt-dlp to fetch and download media from online platforms

FFmpeg to merge video/audio and convert formats if needed

Custom logic to auto-select the best available stream

🔐 Legal Notice & Disclaimer

This software is intended strictly for personal and educational use.

Users are responsible for ensuring that downloads comply with applicable copyright laws.
Downloading copyrighted material without permission may violate the terms of service of the content provider.

🙋‍♂️ Author

Developed by: Mohammad Imran Ali
📍 2025 © All Rights Reserved

🔗 Connect with me on LinkedIn:
https://www.linkedin.com/in/imran-xulmi/

⭐ Feedback & Contributions

Suggestions, improvements, and feature requests are welcome!

Open an issue on this repository

Propose enhancements through pull requests

If this project helped you, please give it a star ⭐ on GitHub!
