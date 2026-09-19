# 🎬 YouTube Bangla Translator

An AI-powered Streamlit application that converts YouTube video transcripts into **natural and easy-to-understand Bangla**.

The app first tries to get available YouTube subtitles. If subtitles are unavailable, it automatically downloads the audio and uses **OpenAI Whisper** to generate the transcript. The transcript is then translated into Bangla using **GPT-4o-mini**.

---

## ✨ Features

* 🎥 YouTube URL বা Video ID support
* 📝 Manual & auto-generated subtitle extraction
* 🎙️ Whisper AI audio transcription fallback
* 🤖 GPT-4o-mini powered Bangla translation
* ✂️ Long transcript automatically chunked
* 🎨 Modern dark Streamlit UI
* 📥 Download translated Bangla text
* 🔐 `.env` based API key management

---

## 🧠 How It Works

```text
YouTube URL / Video ID
          ↓
      Video ID
          ↓
   Search Transcript
          ↓
 ┌──────────────────┐
 │ Subtitle Found?  │
 └───────┬──────────┘
         │
    Yes  │  No
     ↓   │   ↓
Subtitle │ Audio Download
     │   │      ↓
     │   │  Whisper AI
     └───┴──────┐
                ↓
          Original Text
                ↓
        Text Chunking
                ↓
          GPT-4o-mini
                ↓
        🇧🇩 Bangla Text
```

---

## 🛠️ Technologies

* **Python**
* **Streamlit**
* **LangChain**
* **OpenAI GPT-4o-mini**
* **OpenAI Whisper**
* **YouTube Transcript API**
* **yt-dlp**
* **FFmpeg**

---

## 📁 Project Structure

```text
YouTubeTranslator/
│
├── app.py
├── translator.py
├── requirements.txt
├── packages.txt
├── .env
├── .gitignore
└── README.md
```

### Main Files

**`app.py`**
Contains the Streamlit user interface and application workflow.

**`translator.py`**
Contains YouTube URL processing, transcript extraction, Whisper fallback and Bangla translation logic.

**`requirements.txt`**
Contains required Python packages.

**`packages.txt`**
Contains system packages required by Streamlit Cloud, such as FFmpeg.

**`.env`**
Stores the OpenAI API key locally.

> ⚠️ Never upload `.env` to GitHub.

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YouTubeTranslator
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate it

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Key

Create `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 6. Check FFmpeg

```bash
ffmpeg -version
```

### 7. Run the application

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## 🌐 Deploy on Streamlit Cloud

This application can be deployed online using **Streamlit Community Cloud**.

Basic deployment flow:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Deploy app.py
       ↓
Public Streamlit URL
```

For deployment:

1. Push the project to GitHub.
2. Connect GitHub with Streamlit Community Cloud.
3. Select your repository.
4. Select `app.py` as the main file.
5. Add your `OPENAI_API_KEY` inside Streamlit **Secrets**.
6. Deploy the application.

Your app will receive a public URL similar to:

```text
https://your-app-name.streamlit.app
```

> ⚠️ Do not upload `.env` or your OpenAI API key to GitHub.

---

## 📦 Requirements

Example `requirements.txt`:

```text
streamlit
yt-dlp
openai
youtube-transcript-api
langchain-openai
langchain-text-splitters
python-dotenv
```

For Streamlit Cloud, `packages.txt` can contain:

```text
ffmpeg
```

---

## 📌 Supported YouTube Links

### Normal URL

```text
https://www.youtube.com/watch?v=VIDEO_ID
```

### Short URL

```text
https://youtu.be/VIDEO_ID
```

### Shorts

```text
https://www.youtube.com/shorts/VIDEO_ID
```

### Video ID

```text
VIDEO_ID
```

---

## ⚠️ Limitations

* OpenAI API key is required.
* Very long videos may take more time and API usage.
* Whisper audio processing requires FFmpeg.
* Videos without subtitles may require audio transcription.
* Large audio files may exceed Whisper's upload limits.

---

## 🚀 Future Improvements

* 🎬 Generate `.srt` Bangla subtitles
* ⏱️ Preserve subtitle timestamps
* 📄 Export translation as PDF
* 🔊 Bangla text-to-speech
* 🌍 Support multiple target languages
* 💾 Translation history
* 📋 Copy-to-clipboard button
* 🎞️ Generate downloadable Bangla subtitle files

---

## 👨‍💻 Author

**Tuhin Biswas**

Built as a Python, LangChain and OpenAI learning project.

---

## 📄 License

This project is intended for educational and personal use.
