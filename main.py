from flask import Flask, request, render_template, jsonify
import torch
from faster_whisper import WhisperModel
from transformers import pipeline
import os
from pydub import AudioSegment
from pydub.playback import play
import re

# Initialize Flask app
app = Flask(__name__)

# Load models
model_size = "base"
whisper_model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=torch.device('cuda:0') if torch.cuda.is_available() else -1)

# Helper function to chunk text
def chunk_text(text, max_tokens=512):
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Helper function to clean transcribed text
def clean_transcription(text):
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # Remove phrases related to advertisements or unwanted keywords
    unwanted_phrases = [
        "CNN.com will feature iReporter photos",
        "Visit CNN.com/Travel",  # Add more as needed
    ]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")
    # Strip extra spaces
    return text.strip()

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            return "<h3 style='color:red;'>Error: No file uploaded.</h3>", 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return "<h3 style='color:red;'>Error: No file selected.</h3>", 400

        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)

        audio_path = os.path.join("uploads", audio_file.filename)
        audio_file.save(audio_path)

        # Transcribe audio
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)

        # Add progress feedback
        transcribed_text = " ".join([segment.text for segment in segments])

        # Clean up the transcription
        cleaned_text = clean_transcription(transcribed_text)

        # Chunk and summarize text
        chunks = chunk_text(cleaned_text)
        summarized_text = " ".join([
            summarizer(chunk, max_length=50, min_length=35, do_sample=False)[0]['summary_text']
            for chunk in chunks
        ])

        # Clean up uploaded file
        os.remove(audio_path)

        return render_template('result.html', transcription=cleaned_text, summary=summarized_text)
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return "<h3 style='color:red;'>An error occurred while processing the file.</h3>", 500

# Route for recording audio
@app.route('/record', methods=['POST'])
def record():
    try:
        if 'audio_data' not in request.files:
            return "<h3 style='color:red;'>Error: No audio data received.</h3>", 400

        audio_file = request.files['audio_data']
        audio_path = os.path.join("uploads", "recorded_audio.wav")
        audio_file.save(audio_path)

        # Transcribe audio
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        transcribed_text = " ".join([segment.text for segment in segments])

        # Clean up the transcription
        cleaned_text = clean_transcription(transcribed_text)

        # Chunk and summarize text
        chunks = chunk_text(cleaned_text)
        summarized_text = " ".join([
            summarizer(chunk, max_length=100, min_length=35, do_sample=False)[0]['summary_text']
            for chunk in chunks
        ])

        # Clean up uploaded file
        os.remove(audio_path)

        return render_template('result.html', transcription=cleaned_text, summary=summarized_text)
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return "<h3 style='color:red;'>An error occurred while processing the audio.</h3>", 500

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
