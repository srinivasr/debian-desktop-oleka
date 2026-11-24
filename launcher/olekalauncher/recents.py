"""Launch counts, so apps you use often rank higher."""
import json
import os

PATH = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"),
                    "oleka-launcher", "recents.json")


def load(path=PATH):
    """Return {desktop file name: launch count}. Missing/broken file means empty."""
    try:
        with open(path) as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items()}
    except (OSError, ValueError, AttributeError):
        return {}


def record(app, path=PATH):
    counts = load(path)
    key = os.path.basename(app.path)
    counts[key] = counts.get(key, 0) + 1
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(counts, f)
    except OSError:
        pass  # a failed save must not stop a launch


def bonus(app, counts):
    """5 points per launch, capped at 30, so a weak match cannot win on popularity alone."""
    return min(counts.get(os.path.basename(app.path), 0), 6) * 5
