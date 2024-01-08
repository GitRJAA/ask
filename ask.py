#!/usr/bin/env python3
# Query OpenAI with an optional image and a prompt, hear the response read by a voice from ElevenLabs - KFR '23
import random, argparse, base64, requests
import sys,os
from pathlib import Path

VERSION = 0.7

# API TTS
from elevenlabs import generate, stream, set_api_key, voices
sys.path.append(os.path.expanduser('~'))
from my_env import API_KEY_ELEVENLABS, API_KEY_OPENAI
set_api_key(API_KEY_ELEVENLABS)

# Local TTS
import wave, sounddevice, pyaudio
from balacoon_tts import TTS
from huggingface_hub import hf_hub_download
MODEL = 'en_us_hifi92_light_cpu.addon'
model_path = hf_hub_download(repo_id = "balacoon/tts", filename = MODEL)
tts = TTS(model_path)
speaker = tts.get_speakers()[-1]
CHUNK = 1024

base64_image, url, chosen_voice = None, None, None
TEMP_FILE = 'tmp.wav'

# OpenAI API key
api_key_openai = API_KEY_OPENAI

def text_stream(message: str): yield message

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def print_columns(string_list, num_columns:int = 6):
    for i in range(0, len(string_list), num_columns):
        # Truncate each item to 18 characters and get up to n items for each row
        row_items = [s[:18] for s in string_list[i:i + num_columns]]
        # Create a dynamic format string based on the number of items in row_items
        format_string = " ".join(["{:<20}"] * len(row_items))
        print(format_string.format(*row_items))

def flatten_objects(obj_list):
    def convert_and_flatten(data, parent_key='', sep='_'):
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(convert_and_flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)

    flattened_list = []
    for obj in obj_list:
        # If the object is a custom class, convert it to a dictionary first
        if not isinstance(obj, dict):
            obj = vars(obj)  # vars() gets the __dict__ attribute of an object
        flattened_dict = convert_and_flatten(obj)
        flattened_list.append(flattened_dict)
    
    return flattened_list

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=f"{Path(__file__).stem} v{VERSION} Query OpenAI with an optional image and a prompt.")

    parser.add_argument('prompt', nargs='?', type=str, help='The prompt for the query', default=None)

    parser.add_argument('-l', '--list', action='store_true', help='Display a list of valid speaker names')
    parser.add_argument('-i', '--image_path', type=str, help='The path to the either a local image file or http(s) URL (optional)', default=None)

    speech_options = parser.add_mutually_exclusive_group()
    speech_options.add_argument('-s', '--silent', action='store_true', help='Do not use speech')
    speech_options.add_argument('-v', '--voice', help='Specify a speaker by name')
    speech_options.add_argument('-q', '--query', help='Query speaker details by name')

    args = parser.parse_args()

    voice_list = []
    if args.list: # List voices
        print(f"Voice names:")
        for voice in [{'name': 'local'}] + flatten_objects(voices()): 
            voice_list.append(voice['name'])
        print_columns(voice_list)
        print(f"Total voices available: {len(voice_list)}")
        exit()
    elif args.query: # Get voice details
        print(f"Quering voice: {args.query}")
        for voice in flatten_objects(voices()):
            if args.query in voice['name']:

                output = ''
                for key, value in voice.items():
                    if isinstance(value, list):
                        value = ', '.join(value)
                    output += f"{key}: {value}\n"

                print(output)
                exit()
        print(f"Unknown voice: {args.query}")
        exit()
    elif not args.prompt: # No prompt supplied
        parser.print_usage()
        exit()

    if args.image_path: # An image has been specified
        if 'http' in args.image_path: # It's a web request so we supply the URL
            url = args.image_path
        else: # It's a local file so we send the base64 encoded version
            base64_image = encode_image(args.image_path)
            url = f"data:image/jpeg;base64,{base64_image}"

    openai_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_openai}" }

    openai_payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": args.prompt
                    }
                ]}
        ], "max_tokens": 4096 }

    # Add the image to the payload if provided
    if url:
        openai_payload["messages"][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": url
            } })

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=openai_headers, json=openai_payload)

    responseContent = response.json()['choices'][0]['message']['content']
    print(responseContent)

    if args.silent: exit()

    # TTS response
    text = responseContent.strip()

    if not args.voice or 'local' in args.voice:

        samples = tts.synthesize(text, speaker)
        with wave.open(TEMP_FILE, "w") as fp:
            fp.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
            fp.writeframes(samples)

        with wave.open(TEMP_FILE, 'rb') as wf:

            # Initialize PyAudio
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            # Read data in chunks
            data = wf.readframes(CHUNK)
            while len(data) > 0:
                stream.write(data)
                data = wf.readframes(CHUNK)

            # Close and terminate the stream
            stream.close()
            p.terminate()

        os.remove(TEMP_FILE)

    else:
       
        voice_list = flatten_objects(voices())

        for voice in voice_list:
            if args.voice:
                if args.voice.upper() in voice['name'].upper(): chosen_voice = voice

        if not chosen_voice: 
            chosen_voice = random.choice(voice_list)

        audio_stream = generate(
            text = text_stream(text),
            voice = chosen_voice['name'],
            model = "eleven_turbo_v2",
            stream = True )

        stream(audio_stream)

        byline = f"Red by: {chosen_voice['name']}"
        # audio_stream = generate(
        #     text = text_stream(byline),
        #     voice = chosen_voice['name'],
        #     model = "eleven_turbo_v2",
        #     stream = True )
        # stream(audio_stream)

        print (f"\n{byline.replace('Red','Read')} ({chosen_voice['category']} {chosen_voice.get('labels_age')} {chosen_voice.get('labels_accent')} {chosen_voice.get('labels_gender')}) {len(text)} chars = ${(len(text) * 0.25 / 1000):.4f}")
