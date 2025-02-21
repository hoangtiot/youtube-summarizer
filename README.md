# YouTube Video Summarizer

This is a Python application that summarizes YouTube videos using AI. It downloads the audio from a YouTube video, transcribes it to text, and generates a summary using a pre-trained NLP model.

## Features

- Download audio from YouTube videos.
- Transcribe audio to text using Whisper.
- Summarize text using google/gemini-2.0-pro-exp-02-05:free models supported by OpenRouter.ai.
- Simple and intuitive Gradio UI.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/youtube-summarizer.git
   ```
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Update the OpenRouter Api key with your own key
4. Run:
   ```bash
   pip install virtualenv 
   virtualenv my_env
   .\my_env\Scripts\activate
   python ytsum.py
   ```
