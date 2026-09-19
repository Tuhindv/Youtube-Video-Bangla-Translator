import os
import yt_dlp
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1. YouTube URL / Video ID Extractor
# ============================================================

def get_video_id(url_or_id):
    """
    বিভিন্ন ফরম্যাটের YouTube URL বা Video ID থেকে ১১ ডিজিটের Video ID বের করে।
    """
    text = url_or_id.strip()

    if len(text) == 11 and "/" not in text and "?" not in text:
        return text

    if "youtu.be/" in text:
        return text.split("youtu.be/")[1].split("?")[0]

    if "youtube.com/watch?v=" in text:
        return text.split("watch?v=")[1].split("&")[0]

    if "youtube.com/shorts/" in text:
        return text.split("shorts/")[1].split("?")[0]

    if "youtube.com/embed/" in text:
        return text.split("embed/")[1].split("?")[0]

    raise ValueError("সঠিক YouTube Link অথবা Video ID দিন।")


# ============================================================
# 2. Audio Download & Speech-to-Text Fallback (Whisper AI)
# ============================================================

def process_audio_fallback(video_id):
    """
    Subtitle না থাকলে Low Bitrate Audio ডাউনলোড করে OpenAI Whisper দিয়ে ট্রান্সক্রিপ্ট তৈরি করে।
    Windows File Lock (WinError 32) এরর সমাধানের জন্য Safe Handling যুক্ত করা হয়েছে।
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    audio_filename = f"temp_{video_id}.mp3"

    ydl_opts = {
        'format': 'ba/b',
        'outtmpl': f'temp_{video_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '24', # ফাইল সাইজ ছোট রাখার জন্য
        }],
        'quiet': True,
        'no_warnings': True
    }

    try:
        # অডিও ডাউনলোড
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not os.path.exists(audio_filename):
            raise Exception("অডিও ফাইল ডাউনলোড হতে ব্যর্থ হয়েছে।")

        # OpenAI Whisper limits checking (Max 25MB)
        if os.path.getsize(audio_filename) > 25 * 1024 * 1024:
            raise Exception("অডিও ফাইলটি ২৫MB-এর চেয়ে বড়। অত্যন্ত দীর্ঘ ভিডিওর ক্ষেত্রে Whisper সরাসরি প্রসেস করতে পারে না।")

        client = OpenAI()
        
        # ফাইলটি 'with' ব্লকের ভেতরে পড়া হবে যাতে পড়া শেষে ফাইল লক খুলে যায়
        with open(audio_filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return transcription.text, "Auto-detected Audio (Whisper AI)"

    except Exception as e:
        raise Exception(f"অডিও প্রসেস করতে সমস্যা হয়েছে (FFmpeg ইনস্টল করা আছে কিনা নিশ্চিত করুন): {str(e)}")

    finally:
        # Windows-এ [WinError 32] আটকানোর জন্য নিরাপদ ফাইল ডিলিট
        if os.path.exists(audio_filename):
            try:
                os.remove(audio_filename)
            except Exception:
                pass


# ============================================================
# 3. Hybrid Get Transcript (Captions + Audio Fallback)
# ============================================================

def get_transcript(video_id):
    """
    ১. প্রথমে যেকোনো ভাষার Manual বা Auto-generated Subtitle বের করে।
    ২. Subtitle না পাওয়া গেলে অডিও ডাউনলোড করে Whisper AI দিয়ে ট্রান্সক্রিপ্ট বানায়।
    """
    # মেথড ১: Direct Transcript Fetch
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([chunk['text'] for chunk in transcript_data])
        return full_text, "Default Captions"
    except Exception:
        pass

    # মেথড ২: Priority Searching (Manual Subtitle > Auto-generated Subtitle)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Manual Subtitles
        for item in transcript_list:
            if not item.is_generated:
                data = item.fetch()
                full_text = " ".join([chunk['text'] for chunk in data])
                return full_text, f"{item.language} (Manual Subtitle)"

        # Auto-generated Subtitles
        for item in transcript_list:
            if item.is_generated:
                data = item.fetch()
                full_text = " ".join([chunk['text'] for chunk in data])
                return full_text, f"{item.language} (Auto Subtitle)"
    except Exception:
        pass

    # মেথড ৩: Subtitle না থাকলে Audio থেকে Whisper AI দিয়ে টেক্সট তৈরি
    return process_audio_fallback(video_id)


# ============================================================
# 4. Chunking & Translation into Bangla
# ============================================================

def translate_to_bangla(text):
    """
    দীর্ঘ টেক্সটকে (3500 chars) ছোট ছোট টুকরো করে GPT-4o-mini দিয়ে সাবলীল বাংলায় অনুবাদ করে।
    """
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3500,
        chunk_overlap=150
    )
    
    chunks = text_splitter.split_text(text)
    translated_chunks = []

    for chunk in chunks:
        prompt = f"""
You are a professional translator and movie subtitle expert.

Translate the following transcript chunk into natural, fluent Bangla.

Rules:
- Keep the natural dialogue flow and sequence intact.
- Translate into clear, expressive, and easy-to-understand Bangla.
- Preserve character names, locations, numbers, and technical terms correctly.
- Return ONLY the Bangla translation without any explanation or extra meta text.

Transcript Chunk:
{chunk}
"""
        response = model.invoke(prompt)
        translated_chunks.append(response.content.strip())

    return "\n\n".join(translated_chunks)