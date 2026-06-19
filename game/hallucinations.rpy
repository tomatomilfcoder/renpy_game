## Scaffold for the future hallucination mechanic.
## Replace or extend this list later with imported audio paths, for example:
## define hallucination_sounds = imported_hallucination_sounds
define hallucination_sounds = [
    "audio/hallucinations/DS_item_acquired.mp3",
]

define hallucination_min_delay = 12.0
define hallucination_max_delay = 35.0

default hallucination_audio_active = False
default hallucination_next_play_at = 0.0

## Future mechanic should set this flag instead of calling the audio layer directly.
default hallucination_state = False


init python:

    def schedule_next_hallucination_sound():
        global hallucination_next_play_at

        delay = renpy.random.uniform(hallucination_min_delay, hallucination_max_delay)
        hallucination_next_play_at = renpy.get_game_runtime() + delay

    def set_hallucination_state(active):
        global hallucination_state
        global hallucination_audio_active

        hallucination_state = active
        hallucination_audio_active = active

        if active:
            schedule_next_hallucination_sound()

    def poll_hallucination_sound():
        if not hallucination_audio_active or not hallucination_state:
            return

        if not hallucination_sounds:
            return

        if renpy.get_game_runtime() < hallucination_next_play_at:
            return

        renpy.play(renpy.random.choice(hallucination_sounds), channel="sound")
        schedule_next_hallucination_sound()


screen hallucination_sound_loop():
    timer 1.0 repeat True action Function(poll_hallucination_sound)
