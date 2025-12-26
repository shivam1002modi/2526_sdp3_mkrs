#A Simple File Transcription Script using Google Speech-to-Text API
#Speech-to-Text (STT) Implementation in Python

import os
from google.cloud import speech

def transcribe_audio_file(file_path):
    """Transcribe the audio file using the Google Speech-to-Text API."""
    
    # 1. Create a Speech client
    client = speech.SpeechClient()

    # 2. Load the audio file into memory
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    # 3. Configure the audio recognition
    # Replace 'en-US' with your language code if needed (e.g., 'hi-IN' for Hindi)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000, # This must match your audio file's sample rate
        language_code="en-US",
    )

    print(f"Sending audio file '{file_path}' to Google for transcription...")

    # 4. Perform the transcription
    response = client.recognize(config=config, audio=audio)

    # 5. Process the response and print the results
    for result in response.results:
        print("-" * 30)
        print(f"Transcript: {result.alternatives[0].transcript}")
        print(f"Confidence: {result.alternatives[0].confidence:.2f}")

# --- Main Execution ---
if __name__ == "__main__":
    audio_file_name = "audio.wav"  # CHANGE THIS to your audio file name
    
    if not os.path.exists(audio_file_name):
        print(f"Error: Audio file '{audio_file_name}' not found.")
        print("Please place a 16000Hz WAV file in the same folder.")
    else:
        transcribe_audio_file(audio_file_name)

# How to run : python stt_script.py
# Make sure to set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# to point to your Google Cloud service account JSON key file before running the script.
# Example:
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"