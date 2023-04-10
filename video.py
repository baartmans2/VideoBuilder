from moviepy.editor import *
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
import script
import random
from animal import Animal
from enum import Enum
from typing import List
from copy import deepcopy

# region Paths

BACKGROUND_MUSIC_PATH = "BackgroundMusic/"

VIDEO_OUTPUT_PATH = "Output/"

ASSET_PATH = "Assets/"
ACTIVE_PATH = "Active/"

if not os.path.exists(BACKGROUND_MUSIC_PATH):
    os.makedirs(BACKGROUND_MUSIC_PATH)

if not os.path.exists(VIDEO_OUTPUT_PATH):
    os.makedirs(VIDEO_OUTPUT_PATH)

if not os.path.exists(ASSET_PATH):
    os.makedirs(ASSET_PATH)
# endregion


class ClipSize(Enum):
    FULLSCREEN = 0
    VERTICALSPLITSCREEN = 1
    HORIZONTALSPLITSCREEN = 2


class ClipStyle(Enum):
    IMAGE = 0
    VIDEO = 1


class ClipTransition(Enum):
    CROSSFADE_IN = 0,
    CROSSFADE_OUT = 0


class ClipFormat:
    def __init__(self, style: ClipStyle = ClipStyle.IMAGE, size: ClipSize = ClipSize.FULLSCREEN, assets=1, duration=None, overlays: List[ImageClip] = [], path_override=None, transitions: List[ClipTransition] = [ClipTransition.CROSSFADE_IN, ClipTransition.CROSSFADE_OUT]):
        self.style = style
        self.size = size
        self.assets = assets
        self.duration = duration
        self.overlays = overlays
        self.path_override = path_override
        self.transitions = transitions

    def new(self):
        new = deepcopy(self)
        return new

    def add_overlay(self, overlay):
        self.overlays.append(overlay)
        return self

    def set_transitions(self, transitions):
        self.transitions = transitions
        return self

    def set_override(self, path):
        self.path_override = path
        return self

    def set_duration(self, duration):
        self.duration = duration
        return self

    def format_clip(self, paths, duration, video_height=1280, video_width=720):
        clips = []
        path_counter = 0
        # get the assets from paths according to number of assets needed for clip and turn into a array of clips with calculated height and width
        for i in range(self.assets):
            try:
                clip = None
                if self.path_override is None:
                    if self.style == ClipStyle.IMAGE:
                        clip = ImageClip(paths[path_counter])
                    elif self.style == ClipStyle.VIDEO:
                        clip = VideoClip(paths[path_counter])
                else:
                    if self.style == ClipStyle.IMAGE:
                        clip = ImageClip(self.path_override)
                    elif self.style == ClipStyle.VIDEO:
                        clip = VideoClip(self.path_override)

                # resize
                clip = clip.resize(height=video_height)
                (w, h) = clip.size

                # resize clip according to specified size
                if self.size == ClipSize.VERTICALSPLITSCREEN:
                    clip = clip.fx(vfx.crop, x_center=w/2, y_center=h/2,
                                   width=video_width, height=video_height / self.assets)
                elif self.size == ClipSize.FULLSCREEN:
                    clip = clip.fx(vfx.crop, x_center=w/2, y_center=h/2,
                                   width=video_width, height=video_height)
                elif self.size == ClipSize.HORIZONTALSPLITSCREEN:
                    clip = clip.fx(vfx.crop, x_center=w/2, y_center=h/2,
                                   width=video_width / self.assets, height=video_height)

                clips.append(clip)
            except:
                print("Unable to open" + paths[path_counter] + ".")
            # increment path counter to grab next asset supplied. if not enough were supplied, begin to reuse assets.
            path_counter += 1
            if path_counter > (self.assets - 1):
                path_counter = 0

        # build clip according to style
        final_clip = None
        if self.size == ClipSize.FULLSCREEN:
            final_clip = clips[0]
        elif self.size == ClipSize.VERTICALSPLITSCREEN:
            formatted_array = []
            for clip in clips:
                formatted_array.append([clip])
            final_clip = clips_array(formatted_array)
        elif self.size == ClipSize.HORIZONTALSPLITSCREEN:
            final_clip = clips_array(clips)

        # apply overlays
        for overlay in self.overlays:
            final_clip = CompositeVideoClip([final_clip, overlay])

        final_clip = final_clip.set_duration(duration)
        # apply transitions
        for transition in self.transitions:
            if transition == ClipTransition.CROSSFADE_IN:
                final_clip = final_clip.crossfadein(0.15)
            elif transition == ClipTransition.CROSSFADE_OUT:
                final_clip = final_clip.crossfadeout(0.15)

        # apply duration
        if self.duration is not None:
            final_clip = final_clip.set_duration(self.duration)

        return final_clip


def with_duration(clip_format: ClipFormat, duration):
    return clip_format.set_duration(duration)


class Scene:
    def __init__(self, clip_formats: List[ClipFormat] = [], overlays: List[ImageClip] = [], has_audio=True):
        self.clip_formats = clip_formats
        self.overlays = overlays
        self.assets = 0
        self.has_audio = has_audio
        for format in clip_formats:
            self.assets += format.assets

    def new(self):
        new = deepcopy(self)
        return new

    def add_overlay(self, overlay):
        self.overlays.append(overlay)
        return self

    # duration should usually be equal to audio length if it exists
    def build(self, paths, duration, audio=None, video_height=1280, video_width=720):
        # build scene alternating paths, repeat if you run out
        path_counter = 0
        clips = []
        time_remaining_for_clips = duration
        untimed_clips = len(self.clip_formats)
        # calculate time remaining for clips that need to be dynamically assigned durations
        for clip_format in self.clip_formats:
            if clip_format.duration is not None:
                time_remaining_for_clips = time_remaining_for_clips - clip_format.duration
                untimed_clips -= 1

        # build each clip in the scene
        for clip_format in self.clip_formats:
            # number of paths needed for the clip
            path_count = clip_format.assets
            # if number of paths is greater than paths provided, only supply the amount of paths provided, which will lead to reused assets
            if path_count > len(paths):
                path_count = len(paths)

            clip_duration = clip_format.duration
            if clip_format.duration is None:
                clip_duration = time_remaining_for_clips / untimed_clips

            # build clip
            clip = clip_format.format_clip(
                paths[path_counter: path_counter + path_count], clip_duration, video_height, video_width)

            clips.append(clip)
            # update path counter
            path_counter += path_count

            # if reached end of path, begin to reuse old assets
            if path_counter > len(paths) - 1:
                path_counter = 0

        scene = concatenate(clips, method="compose")

        # apply overlays
        for overlay in self.overlays:
            scene = CompositeVideoClip(scene, overlay)

        # if audio exists, apply it

        scene.audio = audio

        scene.set_duration(audio.duration)

        return scene


class Video:
    def __init__(self, name, height=1280, width=720, scenes: List[Scene] = [], overlays: List[ImageClip] = [], background_audio: AudioFileClip = None):
        self.name = name
        self.height = height
        self.width = width
        self.scenes = scenes
        self.overlays = overlays
        self.background_audio = background_audio
        self.assets = 0
        for scene in scenes:
            self.assets += scene.assets

    def add_scene(self, scene):
        self.scenes.append(scene)
        return self

    def set_background_audio(self, audio):
        self.background_audio = audio

    # audio paths should be equal to num of scenes
    def build(self, paths, audioclips):
        path_counter = 0
        audio_counter = 0
        built_scenes: List[Scene] = []

        # build each scene
        for scene in self.scenes:
            # get audio if the scene requires it
            scene_audio = None
            if scene.has_audio:
                scene_audio = audioclips[audio_counter]
                audio_counter += 1

            # get the limit index to grab the amount of assets necessary to build the scene
            paths_high_index = path_counter + scene.assets

            # if more assets are required than are available, send all the new ones that are available
            if paths_high_index > len(paths):
                paths_high_index = len(paths)

            # build the scene and add it to built scenes array
            built_scenes.append(scene.build(
                paths[path_counter: paths_high_index], scene_audio.duration, scene_audio, video_height=self.height, video_width=self.width))

            # increment paths counter to index of next available asset
            path_counter = path_counter + scene.assets

            # reuse assets if out of new ones
            if path_counter > (len(paths) - 1):
                path_counter = 0

        # concatenate built scenes

        final_video = concatenate(built_scenes, method="compose")

        # apply permanent video overlays
        for overlay in self.overlays:
            final_video = CompositeVideoClip(
                [final_video, overlay.set_duration(final_video.duration)])

        # apply background music if it exists
        if self.background_audio is not None:
            final_audio = CompositeAudioClip(
                [final_video.audio, self.background_audio.set_duration(final_video.duration)])
            final_video.audio = final_audio

        return final_video


# region Overlays

OVERLAY_VS_PERM = ImageClip("Overlays/Permanent.png")
OVERLAY_VS_INTRO = ImageClip("Overlays/VS.png")
OVERLAY_VS_INTRO2 = ImageClip("Overlays/Size.png")
OVERLAY_VS_SPEED = ImageClip("Overlays/Speed.png")
OVERLAY_VS_BITE = ImageClip("Overlays/Bite.png")
OVERLAY_VS_DUR = ImageClip("Overlays/Durability.png")
OVERLAY_VS_LETH = ImageClip("Overlays/Lethality.png")
OVERLAY_VS_WINNER = ImageClip("Overlays/Winner.png")

OVERLAY_5_FACTS = ImageClip("Overlays/5Facts.png")
# endregion

# region Clip Formats

# Image Fullscreen Clip
CF_FS_IMG = ClipFormat()

# 2-Image Vertical Splitscreen Clip
CF_SS2_VERT = ClipFormat(
    size=ClipSize.VERTICALSPLITSCREEN, assets=2)

# endregion


# region Scenes

VS_INTRO_SCENE = Scene(
    clip_formats=[CF_SS2_VERT.new().add_overlay(OVERLAY_VS_INTRO).set_transitions([ClipTransition.CROSSFADE_OUT])])
VS_ANIMAL_INTRO_SCENE = Scene(clip_formats=[CF_FS_IMG.new(), CF_FS_IMG.new()]
                              )
VS_SIZE_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_INTRO2), 1), CF_FS_IMG.new(), CF_FS_IMG.new()])
VS_SPD_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_SPEED), 1), CF_FS_IMG.new(), CF_FS_IMG.new()])
VS_BITE_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_BITE), 1), CF_FS_IMG.new(), CF_FS_IMG.new()])
VS_DUR_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_DUR), 1), CF_FS_IMG.new(), CF_FS_IMG.new()])
VS_LETH_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_LETH), 1), CF_FS_IMG.new(), CF_FS_IMG.new()])
VS_FINAL_SCENE = Scene(clip_formats=[with_duration(
    CF_SS2_VERT.new().add_overlay(OVERLAY_VS_WINNER), 3), CF_FS_IMG.new().set_transitions([ClipTransition.CROSSFADE_IN])])

FACTS_INTRO_SCENE = Scene(clip_formats=[CF_FS_IMG.new().add_overlay(
    OVERLAY_5_FACTS).set_transitions([ClipTransition.CROSSFADE_OUT])])
FACTS_SCENE_1 = Scene(clip_formats=[CF_FS_IMG.new()])
FACTS_SCENE_2 = Scene(clip_formats=[CF_FS_IMG.new()])
FACTS_SCENE_3 = Scene(clip_formats=[CF_FS_IMG.new()])
FACTS_SCENE_4 = Scene(clip_formats=[CF_FS_IMG.new()])
FACTS_SCENE_5 = Scene(
    clip_formats=[CF_FS_IMG.new().set_transitions([ClipTransition.CROSSFADE_IN])])

# endregion


# region Videos

ANIMAL_VERSUS_VIDEO = Video("AnimalVS", scenes=[VS_INTRO_SCENE, VS_ANIMAL_INTRO_SCENE, VS_SIZE_SCENE,
                            VS_SPD_SCENE, VS_BITE_SCENE, VS_DUR_SCENE, VS_LETH_SCENE, VS_FINAL_SCENE])

FACTS_VIDEO = Video("AnimalFacts", scenes=[
                    FACTS_INTRO_SCENE, FACTS_SCENE_1, FACTS_SCENE_2, FACTS_SCENE_3, FACTS_SCENE_4, FACTS_SCENE_5])

# endregion


def choose_background_music():
    files = os.listdir(BACKGROUND_MUSIC_PATH)
    filename = random.choice(files)
    background_audio = AudioFileClip(
        BACKGROUND_MUSIC_PATH + filename, fps=44100)
    background_audio = background_audio.fx(afx.volumex, 0.10)

    return background_audio


def gen_animal_facts_video(animal: Animal):
    animalpath = ASSET_PATH + animal.name + "/" + ACTIVE_PATH
    audiopath = script.get_script_audio_path(
        script.ScriptType.FIVE_FACTS, [animal])
    paths = []
    audio_clips = []
    for i in range(6):
        audio_clip = AudioFileClip(
            audiopath + str(i) + ".wav")
        audio_clips.append(audio_clip)
        paths.append(animalpath + str(i) + ".jpg")
    fact_vid = FACTS_VIDEO
    if len(os.listdir(BACKGROUND_MUSIC_PATH)) > 0:
        background_music = choose_background_music()
        fact_vid.set_background_audio(background_music)
    export = fact_vid.build(paths, audio_clips)
    export.write_videofile(VIDEO_OUTPUT_PATH +
                           fact_vid.name + "_" + animal.name + ".mp4", fps=30)


def gen_animal_vs_video(animal1: Animal, animal2: Animal, winner: Animal):
    animal1path = ASSET_PATH + animal1.name + "/" + ACTIVE_PATH
    animal2path = ASSET_PATH + animal2.name + "/" + ACTIVE_PATH
    winnerpath = winner.name + "/"
    audiopath = script.get_script_audio_path(
        script.ScriptType.VERSUS, [animal1, animal2])
    paths = []
    audio_clips = []
    for i in range(8):
        audio_clip = AudioFileClip(
            audiopath + str(i) + ".wav")
        audio_clips.append(audio_clip)
        paths.append(animal1path + str(i) + ".jpg")
        paths.append(animal2path + str(i) + ".jpg")
    vs_video = ANIMAL_VERSUS_VIDEO
    vs_video.scenes[7].clip_formats[1].set_override(
        winnerpath + "7" + ".jpg")
    if len(os.listdir(BACKGROUND_MUSIC_PATH)) > 0:
        background_music = choose_background_music()
        vs_video.set_background_audio(background_music)
    export_video = vs_video.build(paths, audio_clips)
    export_video.write_videofile(VIDEO_OUTPUT_PATH +
                                 vs_video.name + "_" + animal1.name + "_" + animal2.name + ".mp4", fps=30)
