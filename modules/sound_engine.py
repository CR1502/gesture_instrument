import fluidsynth
import os

# Path to your SoundFont
sf_path = os.path.join("assets", "FluidR3_GM", "FluidR3_GM.sf2")

fs = fluidsynth.Synth()
fs.start(driver="coreaudio")  # macOS native sound driver

# Load SoundFont and assign default instruments
sfid = fs.sfload(sf_path)
fs.program_select(0, sfid, 0, 0)   # Channel 0 - default (e.g., Piano)
fs.program_select(1, sfid, 0, 24)  # Channel 1 - default (e.g., Guitar)

# Track channels by hand
channels = {
    "Left": 0,
    "Right": 1
}

# Track active notes
_active_notes = {"Left": [], "Right": []}

# Note name to MIDI mapping
NOTE_MAPPING = {
    "C": 60,
    "D": 62,
    "E": 64,
    "F": 65,
    "G": 67,
    "A": 69,
    "B": 71,
}


def play_sustained_chord(notes, hand="Left"):
    global _active_notes

    stop_chord(hand)  # Stop any previous chord

    channel = channels.get(hand, 0)
    velocity = 100

    midi_notes = [NOTE_MAPPING[n] for n in notes]
    for note in midi_notes:
        fs.noteon(channel, note, velocity)

    _active_notes[hand] = midi_notes


def stop_chord(hand):
    global _active_notes

    channel = channels.get(hand, 0)
    for note in _active_notes[hand]:
        fs.noteoff(channel, note)

    _active_notes[hand] = []


def set_instrument(hand, instrument_number):
    """
    Set MIDI instrument dynamically per hand.
    """
    if hand in channels:
        fs.program_change(channels[hand], instrument_number)