# ask
**_ask_** is a Python script intended for use at the command line in order to ask the OpenAI API a question, optionally including an image, and get the response read by ElevenLabs API. 

```
usage: ask.py [-h] [-l] [-i IMAGE_PATH] [-s | -v VOICE | -q QUERY] [prompt]

ask v0.3 Query OpenAI with an optional image and a prompt.

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
