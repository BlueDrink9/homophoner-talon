import pytest
import sys
from unittest.mock import MagicMock, patch

# List all Talon modules you import
talon_modules = ["talon", "talon.app", "talon.Module", "talon.Context",
                 "talon.actions", "talon.settings"]


for mod in talon_modules:
    sys.modules[mod] = MagicMock()

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from homophoner import find_nearest_homophone, DEFAULT_MODEL, get_cmu_homophones

mock_settings = {
    "user.homophoner_model_name": DEFAULT_MODEL
}
import talon.settings  # this is now the MagicMock
talon.settings.get = lambda name, default=None: mock_settings.get(name)

HOMOPHONE_CANDIDATES: dict[str, list[str]] = {
    "right": ["right", "write", "rite", "wright"],
    "their": ["their", "there", "they're"],
    "to": ["to", "too", "two"],
    "hear": ["hear", "here"],
    "hole": ["hole", "whole"],
    "allowed": ["allowed", "aloud"],
    "brake": ["brake", "break"],
    "buy": ["buy", "by", "bye"],
    "peace": ["peace", "piece"],
    "cell": ["cell", "sell"],
    "sun": ["sun", "son"],
    "knight": ["knight", "night"],
    "flour": ["flour", "flower"],
    "wait": ["wait", "weight"],
}

import talon.actions  # this is now the MagicMock
talon.actions.user.homophones_get = lambda name, default=None: HOMOPHONE_CANDIDATES.get(name)



@pytest.mark.parametrize(
    "input_word, context, expected",
    [
        # --- right / write / rite / wright ---
        ("right",  "correct", "right"),
        ("right",  "left", "right"),
        ("right",  "read", "write"),
        ("right",  "file", "write"),
        ("right",  "religion","rite"),
        ("right",  "builder", "wright"),

        # --- their / there / they're ---
        ("their",  "location", "there"),
        ("their",  "ownership","their"),

        # --- to / too / two ---
        ("to",     "number", "two"),
        ("to",     "excess", "too"),
        ("to",     "much", "too"),
        ("to",     "direction","to"),

        # --- hear / here ---
        ("hear",   "sound", "hear"),
        ("hear",   "location", "here"),

        # --- hole / whole ---
        ("hole",   "complete", "whole"),
        ("hole",   "golf", "hole"),

        # --- allowed / aloud ---
        ("allowed","speak", "aloud"),
        ("allowed","permission","allowed"),

        # --- brake / break ---
        ("brake",  "car", "brake"),
        ("brake",  "destroy", "break"),

        # --- buy / by / bye ---
        ("buy",    "purchase", "buy"),
        ("buy",    "farewell", "bye"),
        ("buy",    "location", "by"),

        # --- peace / piece ---
        ("peace",  "war", "peace"),
        ("peace",  "portion", "piece"),

        # --- cell / sell ---
        ("cell",   "biology", "cell"),
        ("cell",   "market", "sell"),

        # --- sun / son ---
        ("sun",    "family", "son"),
        ("sun",    "planet", "sun"),

        # --- knight / night ---
        ("knight", "medieval", "knight"),
        ("knight", "dark", "night"),
        ("knight", "day", "night"),

        # --- flour / flower ---
        ("flour",  "baking", "flour"),
        ("flour",  "garden", "flower"),

        # --- wait / weight ---
        ("wait",   "mass", "weight"),
        ("wait",   "delay", "wait"),
    ]
)
def test_find_nearest_homophone(input_word, context, expected):
    assert find_nearest_homophone(input_word, context) == expected

from homophoner import get_cmu_homophones  # Adjust import

@pytest.mark.parametrize(
    "word, expected_candidates",
    [
        ("right", ["write", "rite", "wright"]),
        ("their", ["there", "they're"]),
        ("to", ["too", "two"]),
        ("hear", ["here"]),
        ("hole", ["whole"]),
        ("allowed", ["aloud"]),
        ("brake", ["break"]),
        ("buy", ["by", "bye"]),
        ("peace", ["piece"]),
        ("cell", ["sell"]),
        ("sun", ["son"]),
        ("knight", ["night"]),
        ("flour", ["flower"]),
        ("wait", ["weight"]),
    ]
)
def test_cmudict_matches_hardcoded(word, expected_candidates):
    """
    Ensure CMUdict produces at least the candidates we had hardcoded.
    CMUdict may include more words, but all original hardcoded ones should be present.
    """
    cmu_candidates = get_cmu_homophones(word)

    # Make lowercase to match CMUdict's lowercase entries
    cmu_candidates = [w.lower() for w in cmu_candidates]
    expected_lower = [w.lower() for w in expected_candidates]

    for expected_word in expected_lower:
        assert expected_word in cmu_candidates, f"{expected_word} not in CMUdict candidates for {word}"

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from homophoner import (
    init_overrides,
    load_overrides,
    find_nearest_homophone,
    get_candidates,
)

@pytest.fixture
def override_file_patch(tmp_path):
    test_path = tmp_path / "testoverrides.csv"
    patcher = patch("homophoner.get_overrides_file", return_value=test_path)
    with patcher:
        yield test_path

def test_init_override_file(override_file_patch):
    init_overrides()
    assert override_file_patch.exists()
    with open(override_file_patch, "r", encoding="utf-8") as f:
        contents = f.read()
    assert "input_homophone,context_words,correct_replacement_homophone" in contents

def test_load_override_file(override_file_patch):
    test_path = override_file_patch
    init_overrides()
    overrides = load_overrides()
    assert isinstance(overrides, dict)
    assert ("right", "read") in overrides
    assert overrides[("right", "read")] == "write"

def test_resolve_override(override_file_patch):
    test_path = override_file_patch
    init_overrides()
    orig = get_candidates
    with patch("homophoner.get_candidates", side_effect=lambda w: ["right", "rite", "wright"] if w == "right" else orig(w)):
        result = find_nearest_homophone("right", "read")
        assert result == "write"

if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
