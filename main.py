import animal
import script
import sys
import video
import images
from typing import List

args = sys.argv

# args[1]: Video Type
# args[2]: Action
# args[3]: Primary Animal (Or Winner)
# args[4+]: Secondary Animals

VALID_VIDEO_TYPES = ['vs', 'facts']
VALID_ACTIONS = ['images', 'script', 'audio', 'video', 'auto']


def validate_args(type: str, action: str, animals: List[str]) -> bool:
    if type.lower() not in VALID_VIDEO_TYPES:
        print("Invalid Type Argument")
        return False
    if action.lower() not in VALID_ACTIONS:
        print("Invalid Action Argument")
        return False
    for animal_name in animals:
        if not animal.animal_exists(animal_name):
            print("Invalid Animal Name")
            return False
    return True


def gen_script(script_type: script.ScriptType, animals: List[animal.Animal], primary_animal: animal.Animal):
    print("generating script...")
    if script_type == script.ScriptType.VERSUS:
        script.generate_vs_script(animals, primary_animal)
    elif script_type == script.ScriptType.FIVE_FACTS:
        script.generate_facts_script(animals)


def gen_audio(script_type: script.ScriptType, animals: List[animal.Animal]):
    print("generating audio...")
    path = script.get_directory_name(script_type, animals)
    script.get_tts_audio(path)


def gen_video(script_type: script.ScriptType, animals: List[animal.Animal], primary_animal: animal.Animal):
    print("generating video...")
    if script_type == script.ScriptType.VERSUS:
        video.gen_animal_vs_video(animals[0], animals[1], primary_animal)
    elif script_type == script.ScriptType.FIVE_FACTS:
        video.gen_animal_facts_video(primary_animal)


if validate_args(args[1], args[2], args[3:]):
    script_type = None
    animals = []
    primary_animal = animal.get_animal(args[3])
    if args[1] == "vs":
        script_type = script.ScriptType.VERSUS
        for arg in args[4:]:
            animals.append(animal.get_animal(arg))
    elif args[1] == "facts":
        script_type = script.ScriptType.FIVE_FACTS
        animals.append(primary_animal)

    if args[2] == "script":
        gen_script(script_type, animals, primary_animal)
    elif args[2] == "audio":
        gen_audio(script_type, animals)
    elif args[2] == "video":
        gen_video(script_type, animals, primary_animal)
    elif args[2] == "images":
        images.download_images(animals)
    elif args[2] == "auto":
        # get images
        images.download_images(animals)
        # make script
        gen_script(script_type, animals, primary_animal)
        # make audio
        gen_audio(script_type, animals)
        # make video
        gen_video(script_type, animals, primary_animal)
