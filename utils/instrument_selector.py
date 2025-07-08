import json
import os


def select_instruments():
    path = os.path.join(os.path.dirname(__file__), "..", "config", "selected_instruments.json")

    if not os.path.exists(path):
        raise FileNotFoundError("Instrument selection not found. Please choose instruments from the web UI.")

    with open(path, "r") as f:
        data = json.load(f)

    return {
        "Left": int(data.get("left_instrument", 0)),
        "Right": int(data.get("right_instrument", 0)),
    }