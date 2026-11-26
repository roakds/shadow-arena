"""Reading and writing the high score file."""
import json

import settings as cfg


def load_high_score():
    """Return the saved high score or 0 if there is no valid file."""
    try:
        text = cfg.HIGH_SCORE_FILE.read_text(encoding="utf-8")
        return int(json.loads(text)["high_score"])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def save_high_score(score):
    """Write the high score to disk; ignore file system errors."""
    try:
        cfg.HIGH_SCORE_FILE.write_text(
            json.dumps({"high_score": score}), encoding="utf-8"
        )
    except OSError:
        return
