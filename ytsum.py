import gradio as gr
from yt_dlp import YoutubeDL
import whisper
import requests



# Step 1: Download audio from YouTube
def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return "audio.mp3"

# Step 2: Transcribe audio to text
def transcribe_audio(audio_file):
    model = whisper.load_model("base")  # Use "small", "medium", or "large" for better accuracy
    result = model.transcribe(audio_file)
    return result["text"]

# Step 3: Summarize text using OpenRouter.ai API
def summarize_text_with_openrouter(text):
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer OPENROUTER_API_KEY",  # Replace with your OpenRouter API key
        "Content-Type": "application/json"
    }

    # Payload for the API request
    payload = {
        "model": "google/gemini-2.0-pro-exp-02-05:free",  # Specify the model
        "messages": [
            {"role": "system", "content": """
              You are an AI assistant tasked with summarizing YouTube video transcripts. Provide concise, informative summaries that capture the main points of the video content.
            Instructions:
            1. Summarize the transcript in a single concise paragraph.
            2. Focus on the spoken content (Text) of the video."""},
            {"role": "user", "content": f"Summarize the following text:\n{text}"}
        ]
    }

    # Make the API request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Inspect the API response
    response_data = response.json()
    print("API Response:", response_data)  # Debugging

    # Handle the response
    if "choices" in response_data:
        return response_data["choices"][0]["message"]["content"]
    elif "error" in response_data:
        return f"API Error: {response_data['error']['message']}"
    else:
        return "Unexpected API response format."
    # except requests.exceptions.HTTPError as err:
    #     return f"HTTP Error: {err}"
    # except Exception as err:
    #     return f"Error: {err}"

# Main function to summarize YouTube video
def summarize_youtube_video(youtube_url):
    # Step 1: Download audio
    audio_file = download_audio(youtube_url)
    
    # Step 2: Transcribe audio to text
    text = transcribe_audio(audio_file)
    
    # Step 3: Summarize text using OpenRouter.ai
    summary = summarize_text_with_openrouter(text)
    
    return summary

# Gradio Interface
interface = gr.Interface(
    fn=summarize_youtube_video,
    inputs="text",
    outputs="text",
    title="YouTube Video Summarizer",
    description="Enter a YouTube URL to get a summary of the video."
)

# Launch the app
interface.launch()