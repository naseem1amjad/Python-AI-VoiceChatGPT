#Developed by Naseem Amjad urdujini@gmail.com [Software Engineer]
import openai
import os

import pyaudio
import wave

import warnings
warnings.filterwarnings("ignore")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Set parameters for recording
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open microphone stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print(f"{bcolors.OKCYAN}Listening...")

# Record audio data
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print(f"{bcolors.OKCYAN}Finished Listening.")

# Stop the stream and close the audio object
stream.stop_stream()
stream.close()
audio.terminate()

# Save the audio data to a WAV file
wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)
wave_file.writeframes(b''.join(frames))
wave_file.close()

from google.cloud import speech_v1p1beta1 as speech

# Set up authentication
client = speech.SpeechClient.from_service_account_json('key.json')

# Load audio file
with open('output.wav', 'rb') as audio_file:
    content = audio_file.read()

# Configure recognition settings
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,
    language_code='en-US'
)

# Perform the transcription
response = client.recognize(config=config, audio=speech.RecognitionAudio(content=content))

suna=""
# Print the transcription
for result in response.results:
    suna=result.alternatives[0].transcript
    


if suna is None or len(suna) == 0:
    print(f"{bcolors.FAIL}Nothing heard")
    exit()

print(f"{bcolors.OKGREEN}{suna}")

# Set your API key as an environment variable
openai.api_key = "sk-USE-YOUR-OWN-KEY"

# Generate a response from ChatGPT
model_engine = "text-davinci-003"
question = suna
prompt = "Describe " + question
print ("You asked about "+question)

# Generate a response
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
)

response = completion.choices[0].text
print(f"{bcolors.BOLD}{response}")  

from google.cloud import texttospeech

# Set the path to the service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key4speech.json"

# Set up Google Cloud Text-to-Speech API client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
input_text = texttospeech.SynthesisInput(text=response)

# Select the language and voice to be used for synthesis
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)

# Select the audio format
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Generate the request and get the response
response = client.synthesize_speech(
    input=input_text,
    voice=voice,
    audio_config=audio_config
)

# Write the response audio content to an MP3 file
with open("output.mp3", "wb") as out_file:
    out_file.write(response.audio_content)

#print("Audio content written to file 'output.mp3'")

# Play the MP3 file
import playsound
playsound.playsound("output.mp3")



    
