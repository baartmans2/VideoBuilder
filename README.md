# VideoBuilder

A semi-declarative interface for easily defining video formats using MoviePy, and tool and automatically generating videos in Python. Utilizes:

- Moviepy
- GPT-3 for script generation
- ElevenLabs Voice AI for generating narration
- Google Custom Search API for automatically retrieving images.
  It is currently designed towards automatically creating short, educational wildlife videos aimed towards children.

## Quickstart Guide

1. Clone the project and cd into the project directory:

```
cd VideoBuilder/
```

2. Make sure you the following packages installed:

- [moviepy](https://pypi.org/project/moviepy/)
- [openai](https://github.com/openai/openai-python)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [elevenlabslib](https://github.com/lugia19/elevenlabslib)

3. Create a .env file supplied with the environment variables specified in .env.example
4. (Optional) Create a folder titled "BackgroundMusic" and put any background music you'd like in your videos in the folder. Must be in mp3 format.
5. Run the program:

```
python3 main.py [video-type] [action-type] [primary animal] [animal 1] [animal 2]
```

`video-type` : The type of video you want to generate material for. Available options are:

- `-vs` : A video evaluating the winner of a hypothetical fight between two animals. Requires
- `-facts`: A video explaining 5 fun facts about a specific animal.

`action-type` : The type of action you want to Perform. Available options are:

- `-images` :downloads images of all animals provided)
- `-script` :generates a script file for the video)
- `-audio` :requires an existing script, downloads generates and downloads audio for the video's narration)
- `-video` :generates a script file for the video).
- `-auto` : does all of the previous four actions. NOTE: This command is currently highly susceptible to error: Google Images sometimes provides images that are unreadable by the program. The text and voice generation is also susceptible to generation and pronunciation errors from time to time. It is better to run one command for each step, and then verify that each step worked properly, as well as edit the script, provide custom images, etc.

`primary animal`: For versus videos, the name of the winning animal of the fight. For facts videos, the animal the video is about. Must match a listed animal in the file `animals.csv` .

`animal 1/2`: These arguments are only required for versus videos. Specifies all the animals in the video (including the animal, and the order in which they will be presented in the video.

Example run commands:

```
python3 main.py -facts -auto Elephant

python3 main.py -vs -script "Mountain Lion" Wolf "Mountain Lion"
```
