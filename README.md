
While learning Machine Learning on YouTube last week, I discovered that the platform doesn't display the total duration of a playlist. This makes it difficult to estimate the time commitment required. To address this, I developed a tool to calculate it, and this repository contains the resulting project.

# 🎬 YouTube Playlist Duration Calculator

> A beautiful desktop application built with Python and Tkinter that calculates the total duration of YouTube playlists with a modern, user-friendly interface.



---

## ✨ Features

* **Modern GUI:** Clean, intuitive interface with contemporary design.
* **Comprehensive Statistics:** Get detailed analytics including average, longest, shortest, and median video durations.
* **Progress Tracking:** Real-time progress updates during calculation.
* **Export Functionality:** Save results to text files for future reference.
* **Error Handling:** Robust error handling with user-friendly messages.
* **Multiple Input Formats:** Supports playlist URLs and direct playlist IDs.
* **Batch Processing:** Efficiently handles large playlists with thousands of videos.

---

## 🚀 Installation

### Option 1: Run from Source

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/youtube-playlist-calculator.git](https://github.com/yourusername/youtube-playlist-calculator.git)
    cd youtube-playlist-calculator
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up YouTube API Key:**
    * Go to the [Google Cloud Console](https://console.cloud.google.com/).
    * Create a new project or select an existing one.
    * Enable the **YouTube Data API v3**.
    * Create credentials (**API Key**).
    * Create a `.env` file in the project directory with the following content:
      ```ini
      YOUTUBE_API_KEY=your_api_key_here
      ```

4.  **Run the application:**
    ```bash
    python playlist_calculator.py
    ```

### Option 2: Download Executable

For Windows users, you can download the pre-built executable from the **Releases** section of this repository.

1.  Download the latest `.exe` file.
2.  Create a `.env` file in the same directory as the executable with your YouTube API key.
3.  Double-click the executable to run.

---

## 🔧 Building Executable

To create your own executable using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Create the executable
pyinstaller --onefile --windowed --icon=icon.ico playlist_calculator.py
```
**📋 Requirements**

* Python 3.7 or higher
* YouTube Data API v3 key (free from Google Cloud Console)
* Internet connection for API requests

**🛠️ Dependencies**

* google-api-python-client: YouTube API integration
* isodate: ISO 8601 duration parsing
* python-dotenv: Environment variable management
* pillow: Image processing (future features)
* tkinter: GUI framework (included with Python)

### 🎯 Usage

1 **Launch the application**

2 **Enter API Key (first time only):**
* If no .env file exists, the app will prompt for your API key
* Click "Open Google Console" for direct access to API setup

3 **Enter Playlist URL or ID:**

* Full YouTube playlist URL: https://www.youtube.com/playlist?list=PLxxxxxx
* Direct playlist ID: PLxxxxxx

4 **Click "Calculate Duration"**

5 **View Results:**

* Total duration in human-readable format
* Comprehensive statistics
* Video processing summary

6 **Export Results (optional):**
* Save detailed report to a text file

## 📊 What You Get

* **Total Duration:** Complete playlist length in days, hours, minutes, and seconds.
* **Video Statistics:**
    * Number of videos processed
    * Average video duration
    * Longest and shortest videos
    * Median duration
* **Processing Summary:** Success and failure counts for video analysis.
* **Export Option:** Save all results to a formatted text file.

---

## 🔐 API Key Setup

### Getting Your YouTube API Key

1.  Visit the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Navigate to **APIs & Services → Library**.
4.  Search for and enable the **YouTube Data API v3**.
5.  Go to **APIs & Services → Credentials**.
6.  Click **Create Credentials → API Key**.
7.  Copy your new API key.

### Setting Up the .env File

Create a `.env` file in the project's root directory and add your API key:

```ini
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
## 🤝 Contributing

Contributions are welcome!

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature/amazing-feature`
3.  Commit your changes: `git commit -m "Add amazing feature"`
4.  Push to the branch: `git push origin feature/amazing-feature`
5.  Open a Pull Request.

---

## 📝 License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

## 🐛 Known Issues

* Private and deleted videos are automatically skipped.
* Very large playlists (10,000+ videos) may take several minutes to process.
* API rate limits may affect processing speed for extremely large playlists.

---

## 🔮 Future Enhancements

- [ ] Playlist comparison feature
- [ ] Data visualization with charts and graphs
- [ ] Support for multiple playlists at once
- [ ] CSV export option
- [ ] Playlist analysis history
- [ ] Dark mode theme
- [ ] System tray integration

---

## 📞 Support

If you encounter any issues or have questions:

1.  Check the **Issues** page first.
2.  Create a new issue with detailed information.
3.  Include your Python version and operating system.

---

## 🙏 Acknowledgments

* Google for the YouTube Data API v3.
* The Python community for its excellent libraries.
* All contributors and users who provide feedback.

---

<p align="center">
  Made with ❤️ for YouTube playlist analysis.
  <br>
  ⭐ Don’t forget to star this repository if you found it helpful! ⭐
</p>
