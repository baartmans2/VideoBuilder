import openai
import json
import os
from enum import Enum
from animal import Animal
from typing import List
from elevenlabslib import *
from dotenv import load_dotenv

load_dotenv()

openai.api_key = str(os.environ.get("OPENAI_API_KEY"))
model_engine = "text-davinci-003"

ELEVENLABS_API_KEY = str(os.environ.get("ELEVENLABS_API_KEY"))

TTS_USER = ElevenLabsUser(ELEVENLABS_API_KEY)
TTS_VOICE = TTS_USER.get_voices_by_name("Antoni")[0]

FACTS_PROMPT = '''\
Write a script for a short narrated video called "Five Facts You Didn't Know About the {animal_name}. The format requirements for the script are as follows:
Line 1 format: "Five Facts You Didn't Know About the {animal_name}"
Lines 2-6 format: "[The Fact]"
Lastly, after you've generated the script, format it like this, with a newline character at the end of each line:

[Line 1 Text]

[Line 2 Text]

[Line 3 Text]

[Line 4 Text]

[Line 5 Text]

[Line 6 Text]

In the Line Text, ONLY include the words that will be spoken by the narrator, do not add any labels.
    '''

VERSUS_PROMPT = '''\
Write a script for a short narrated video about who would win a fight between the following animals: [Animal 1] vs [Animal 2]. The animals to use will be provided to you in this format: [Animal Name, Average Weight (lbs), Top Speed (mph), Bite Force (psi)]. 
    

Here are the animals to use for the script:
Animal 1: [{animal1_name},  {animal1_weight}, {animal1_speed}, {animal1_bite}]
Animal 2: [{animal2_name},  {animal2_weight}, {animal2_speed}, {animal2_bite}]
Winning Animal: {winner_name}
    
Use the extra data in the comparisons for lines 3 through 5. The winning animal will also be provided to you at the end of this prompt. The format requirements for the script are as follows:
    
Line 1 format: "Who would win in a fight: [Animal 1] versus [Animal 2]?"
Line 2 format: "[Brief description of Animal 1]. [Brief description of Animal 2]" Include where in the world the animals live. Do not include the numeric data for weight, speed, or bite force in this.
Line 3 format: "Size: [Plural of Animal 1] weigh [Animal 1 average weight, pounds]. [Plural of Animal 2] weigh [Animal 2 average weight, pounds], [whether Animal 2's average weight is larger or smaller than Animal 1's average weight]."
Line 4 format: "Speed: The [Animal 1] has a top speed of [Animal 1 top speed in miles per hour]. The [Animal 2] has a [faster or slower] top speed of [Animal 2 top speed in miles per hour]."
Line 5 format: "Bite Force: The [Animal 1] has a bite force of [Animal 1 bite force, psi], while the [Animal 2] has a bite force of [Animal 2 bite force, psi]." For either animal, if the bite force is 0, say "The bite force of the [Animal with unknown bite force] is unknown."
Line 6 format: "Durability: [Describe Animal 1's skin thickness and features that would aid in its defense in a fight, or lack thereof] [Describe Animal 2's skin thickness and features that would aid in its defense in a fight, or lack thereof]."
Line 7 format: "Lethality: [Describe Animal 1's aggressiveness and deadliness, or lack thereof]. [Describe Animal 2's aggressiveness and deadliness, or lack thereof].
Line 8 format: "Now, the moment we've all been waiting for, who would win? [The winning animal, the main reason(s) it would win, or that the matchup would likely end in a tie]. That answers the question..."
    
Lastly, after you've generated the script, format it like this, with a newline character at the end of each line:

[Line 1 Text]

[Line 2 Text]

[Line 3 Text]

[Line 4 Text]

[Line 5 Text]

[Line 6 Text]

[Line 7 Text]

[Line 8 Text]

    In the Line Text, ONLY include the words that will be spoken by the narrator, do not add any labels.
    '''


SCRIPTS_PATH = "Scripts/"

AUDIO_PATH = "Audio/"

if not os.path.exists(SCRIPTS_PATH):
    os.makedirs(SCRIPTS_PATH)


class ScriptType(Enum):
    VERSUS = "VS",
    FIVE_FACTS = "FACTS"


def generate_facts_script(animals: List[Animal]):
    if len(animals) < 1:
        print("No animal provided.")
        return
    animal1 = animals[0]
    prompt = FACTS_PROMPT.format(animal_name=animal1.name)
    lines = get_chatgpt_response(prompt)
    write_script_to_file(lines, get_directory_name(
        ScriptType.FIVE_FACTS, animals))


def get_directory_name(type: ScriptType, animals: List[Animal]) -> str:
    directory_name = SCRIPTS_PATH
    directory_name = directory_name + type.value[0]
    for animal in animals:
        directory_name = directory_name + "_" + animal.name
    directory_name = directory_name + "/"
    return directory_name


def get_script_path(directory_name) -> str:
    return directory_name + "script.json"


def get_script_audio_path(type: ScriptType, animals: List[Animal]) -> str:
    return get_directory_name(type, animals) + "Audio/"


def generate_vs_script(animals: List[Animal], winner: Animal):
    animal1 = animals[0]
    animal2 = animals[1]
    prompt = VERSUS_PROMPT.format(animal1_name=animal1.name, animal1_weight=animal1.weight, animal1_speed=animal1.speed, animal1_bite=animal1.bite,
                                  animal2_name=animal2.name, animal2_weight=animal2.weight, animal2_speed=animal2.speed, animal2_bite=animal2.bite, winner_name=winner.name)

    lines = get_chatgpt_response(prompt)
    write_script_to_file(lines, get_directory_name(
        ScriptType.VERSUS, animals))

    return get_directory_name(ScriptType.VERSUS, animals)


def write_script_to_file(lines, path):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + "script.json", 'w') as f:
        json.dump(lines, f)


def read_script_from_file(script_path):
    if not os.path.exists(script_path):
        return []
    with open(script_path) as f:
        return json.load(f)


def get_chatgpt_response(prompt):
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0
    )
    lines = str(completion.choices[0].text).strip().split("\n")
    for line in lines:
        line.strip()
        if line == '':
            lines.remove(line)
    return lines


def download_audio(bytes, script_directory, filename):
    audio_dir = script_directory + AUDIO_PATH
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    full_path = audio_dir + filename + ".wav"
    with open(full_path, mode='bx') as f:
        f.write(bytes)

    print("Successfully Downloaded " + filename)


def get_tts_audio(script_directory):
    script_path = get_script_path(script_directory)
    print(script_path)
    if not os.path.exists(script_path):
        print("No script exists in directory " +
              script_directory + ". Please generate one.")
        return
    script = read_script_from_file(script_path)
    if script == []:
        print("No script found at " + script_path +
              ". Please create one and try again")
        return
    for index, line in enumerate(script):
        filename = str(index)
        if os.path.exists(script_directory + 'Audio/' + filename + ".wav"):
            print(
                "Line " + filename + " of the script is already downloaded. Delete it if you want to regenerate")
        else:
            download_audio(TTS_VOICE.generate_audio_bytes(
                line), script_directory, filename)
