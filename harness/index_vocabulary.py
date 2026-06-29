"""Load contract/index_vocabulary.json for renderers and client constants."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(ROOT, "contract", "index_vocabulary.json")
_CACHE = None


def load_index_vocabulary():
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def quadrant_editorial():
    """Return {quad_id: {label, tagline, lead, one_liner}}."""
    return load_index_vocabulary().get("quadrants", {})


def quadrant_labels():
    q = quadrant_editorial()
    return {k: v.get("label", k) for k, v in q.items()}


def quadrant_taglines():
    q = quadrant_editorial()
    return {k: v.get("tagline", "") for k, v in q.items()}
