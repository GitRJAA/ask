# ask
**_ask_** is a very simple Python script intended to be used at the command line in order to ask the <a href="https://platform.openai.com/">OpenAI</a> API a question, optionally including an image, and then have the response realistically read by a voice from <a href="https://elevenlabs.io/">ElevenLabs</a>. 

As written, it expects `my_env.py` in your home directory; its contents defining API keys as follows:
```
API_KEY_OPENAI = '<insert_your_OpenAI_API_key_here>'
API_KEY_ELEVENLABS = '<insert_your_ElevenLabs_API_key_here>'
```

### Example installation:
```
chmod +x ask.py
mv ask.py ~/.local/bin/ask
```

## Usage
```
usage: ask [-h] [-l] [-i IMAGE_PATH] [-s | -v VOICE | -q QUERY] [prompt]

ask v0.4 Query OpenAI with an optional image and a prompt.

positional arguments:
  prompt                The prompt for the query

options:
  -h, --help            show this help message and exit
  -l, --list            Display a list of valid speaker names
  -i IMAGE_PATH, --image_path IMAGE_PATH
                        The path to the either a local image file or http(s) URL (optional)
  -s, --silent          Do not use speech
  -v VOICE, --voice VOICE
                        Specify a speaker by name
  -q QUERY, --query QUERY
                        Query speaker details by name
```
