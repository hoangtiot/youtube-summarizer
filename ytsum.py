import gradio as gr
from yt_dlp import YoutubeDL
import whisper
import requests



# Step 1: Get video details from YouTube (audio and thumbnail)
def get_video_details(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'writethumbnail': True,  # Download thumbnail
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        thumbnail_url = info_dict.get('thumbnail')
        title = info_dict.get('title')
    return "audio.mp3", thumbnail_url, title


# Step 2: Transcribe audio to text
def transcribe_audio(audio_file):
    model = whisper.load_model("base")  # Use "small", "medium", or "large" for better accuracy
    result = model.transcribe(audio_file)
    return result["text"]

# Function to generate text using Gemini API
def generate_text(prompt):
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
            {"role": "user", "content": f"Summarize the following text:\n{prompt}"}
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



# Main function to summarize YouTube video
def summarize_video(transcription):
    try:
        # Generate summary
        prompt = f"Summarize the following video transcription in a way that provide knowledge:\n{transcription}"
        summary = generate_text(prompt)
        return summary
    except Exception as e:
        return f"Error: {str(e)}"


# Function to generate an introduction
def generate_introduction(transcription):
    try:
        # Generate introduction
        prompt = f"Create an engaging introduction based on the following video transcription. Make the user curious to learn more:\n{transcription}"
        introduction = generate_text(prompt)
        return introduction
    except Exception as e:
        return f"Error: {str(e)}"

# Function to answer user questions
def answer_question(transcription, question):
    try:
        # Generate answer
        prompt = f"Based on the following video transcription, answer the following question in a way that helps the user study:\nTranscription:\n{transcription}\nQuestion:\n{question}"
        answer = generate_text(prompt)
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate a quiz
def generate_quiz(transcription):
    try:
        # Generate quiz
        prompt = f"Create a small quiz with 3 questions based on the following video transcription. Format the quiz as follows:\n1. Question 1\n2. Question 2\n3. Question 3\nTranscription:\n{transcription}"
        quiz = generate_text(prompt)
        return quiz
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio UI
def youtube_summarizer(youtube_url, action, question=None):
    # Get video details
    audio_file, thumbnail_url, title = get_video_details(youtube_url)
    if not thumbnail_url:
        return f"Error: Invalid YouTube URL or unable to fetch details."

    # Display video details
    video_details = f"**Title:** {title}\n\n**Thumbnail:** ![Thumbnail]({thumbnail_url})"

    # Transcribe audio
    transcription = transcribe_audio(audio_file)
    if transcription.startswith("Error"):
        return video_details, transcription, "", "", ""

    # Initialize outputs
    summary = ""
    introduction = ""
    answer = ""
    quiz = ""

     # Handle actions
    if action == "Summarize":
        summary = summarize_video(transcription)
    elif action == "Introduction":
        introduction = generate_introduction(transcription)
    elif action == "Ask a Question":
        answer = answer_question(transcription, question)
    elif action == "Test":
        quiz = generate_quiz(transcription)

    return video_details, summary, introduction, answer, quiz

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# YouTube Video Summarizer")
    gr.Markdown("Enter a YouTube URL to get started. Use the buttons to summarize, generate an introduction, ask questions, or take a quiz.")

    with gr.Row():
        youtube_url = gr.Textbox(label="YouTube URL", placeholder="Enter a YouTube URL")
        question = gr.Textbox(label="Ask a Question", placeholder="Enter your question (optional)")

    with gr.Row():
        summarize_btn = gr.Button("Summarize")
        intro_btn = gr.Button("Introduction")
        question_btn = gr.Button("Ask a Question")
        test_btn = gr.Button("Test")

    with gr.Row():
        video_details = gr.Markdown(label="Video Details")
        summary = gr.Textbox(label="Summary")
        introduction = gr.Textbox(label="Introduction")
        answer = gr.Textbox(label="Answer")
        quiz = gr.Textbox(label="Quiz")

    # Set button actions
    summarize_btn.click(
        youtube_summarizer,
        inputs=[youtube_url, gr.State("Summarize"), question],
        outputs=[video_details, summary, introduction, answer, quiz],
    )
    intro_btn.click(
        youtube_summarizer,
        inputs=[youtube_url, gr.State("Introduction"), question],
        outputs=[video_details, summary, introduction, answer, quiz],
    )
    question_btn.click(
        youtube_summarizer,
        inputs=[youtube_url, gr.State("Ask a Question"), question],
        outputs=[video_details, summary, introduction, answer, quiz],
    )
    test_btn.click(
        youtube_summarizer,
        inputs=[youtube_url, gr.State("Test"), question],
        outputs=[video_details, summary, introduction, answer, quiz],
    )

# Launch the app
demo.launch()