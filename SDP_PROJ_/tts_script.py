#Text-to-Speech (TTS) Implementation in Python
#This code will take a string of text and create an audio file (output.mp3) that you can play.
#install this librerary : pip install google-cloud-texttospeech

from google.cloud import texttospeech

def synthesize_text(text_to_speak, output_filename="output.mp3"):
    """Synthesizes speech from the input string of text."""
    
    # 1. Create a Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # 2. Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)

    # 3. Choose the voice parameters (language, gender, etc.)
    # You can explore many other voices on the GCP documentation.
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", # Language
        name="en-US-Standard-C", # Specific voice name
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE # Gender
    )

    # 4. Select the type of audio file you want
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    print(f"Synthesizing text: '{text_to_speak}'")

    # 5. Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # 6. The response's audio_content is the binary audio data.
    with open(output_filename, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_filename}"')

# --- Main Execution ---
if __name__ == "__main__":
    my_project_text = (
        "Hello! I am a speech synthesis feature. "
        "This is an example of text-to-speech in Python using the Google Cloud API."
    )
    synthesize_text(my_project_text)

    # run the script : python tts_script.py