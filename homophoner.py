from gensim.utils import simple_preprocess
import gensim.downloader as api
from functools import cache
import numpy as np

from talon import app, Module, Context, actions, settings

mod = Module()
ctx = Context()

DEFAULT_MODEL = "glove-wiki-gigaword-50"

mod.setting(
    "homophoner_model_name",
    type=str,
    default=DEFAULT_MODEL,
    desc="""Name of the gensim model to use for comparing words, larger ones will take up more disk space and be slightly slower but will be more accurate. Aim for a word2vec style model, so that it learns semantic meanings as opposed to just cooccurrence.
    See https://github.com/piskvorky/gensim-data?tab=readme-ov-file#models for available model options
    Recommendations other than the default:
        * The best one for accuracy, at 1.6 gigabytes, is word2vec-google-news-300
        * glove-wiki-gigaword-300 is 400 megabytes, and should be somewhat more flexible than the default.
    """,
)


@cache
def load_model(model_name: str | None = None):
    """Load the embedding model once and memoize it."""
    print("Homophoner is downloading/loading word model, this might take a while")
    if not model_name:
        model_name: str | None = settings.get("user.homophoner_model_name")
    return api.load(model_name)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Return cosine similarity between two vectors."""
    denom = (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    if denom == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / denom)


def find_nearest_homophone(
    input_word: str,
    context: str,
) -> str:
    """
    Pick the candidate whose meaning is closest to the context word
    in the given embedding space.

    - Always returns exactly one candidate.
    - If two are tied, returns the first among the closest.
    """
    candidates = get_candidates(input_word)
    print(candidates)
    if not candidates:
        print(f"No homophones registered for '{input_word}'")
        return input_word

    model = load_model()
    #  gensim.utils.simple_preprocess(context, deacc=True, min_len=2, max_len=35)

    # Context word(s) must exist in model, otherwise we just return the first candidate
    context_vec = get_context_vector(context, model)
    if context_vec is None:
        return candidates[0]

    # TODO: add a user customizable CSV that lets users specify a particular replacement for a particular context word, in case the model gets it wrong
    scored = []
    for cand in candidates:
        if cand in model:
            score = cosine_similarity(model[cand], context_vec)
        else:
            # Words missing from model score lowest
            score = float("-inf")
        scored.append((score, cand))

    # Sort by score DESC, but keep stable ordering for ties
    scored.sort(key=lambda x: x[0], reverse=True)
    print(scored)
    return scored[0][1]

def get_context_vector(context: str, model):
    """Return averaged vector for multi-word context, or None if nothing usable."""
    tokens = simple_preprocess(context, deacc=True, min_len=2)
    vecs = [model[t] for t in tokens if t in model]
    if not vecs:
        return None
    return np.mean(vecs, axis=0)


# def get_candidates(input_word: str) -> list[str]:
#     """Return the list of homophones for a given word, or empty if unknown."""
#     homophones: list[str] | None = actions.user.homophones_get(input_word)
#     return homophones

def get_candidates(input_word: str) -> list[str]:
    """
    1. Try Talon user-defined homophones
    2. If none, try CMUdict
    3. If none, return None
    """
    # Talon user homophones take priority
    manual = actions.user.homophones_get(input_word)
    if manual:
        return manual

    # Fallback: CMUdict lookup
    cmu = get_cmu_homophones(input_word)
    if cmu:
        return [input_word] + cmu  # ensure input stays first

    # Nothing at all – avoid empty list failures
    return None


def get_cmu_homophones(word: str) -> list[str]:
    """Return all CMUdict homophones for a word, excluding itself.

    CMUdict homophones are homophones based on phoneme signature mapping, which is much more flexible than the talon hardcoded lists, making them great has a fallback candidate source
    """
    try:
        homophones = load_cmudict()
    except LookupError as ex:
        import nltk
        nltk.download('cmudict')

    # Find all phoneme keys containing this word
    results = set()
    for words in homophones.values():
        if word in words:
            results.update(words)

    results.discard(word)  # remove input itself
    return sorted(results)


@cache
def load_cmudict():
    """Load CMUdict once and return mapping: phoneme_signature -> [words...]"""
    try:
        from nltk.corpus import cmudict
    except LookupError:
        import nltk
        nltk.download("cmudict")
        from nltk.corpus import cmudict

    entries = cmudict.dict()
    homophones = {}

    for word, phonemes in entries.items():
        # phonemes is a list of lists if multiple pronunciations exist
        for p in phonemes:
            key = " ".join(p)  # e.g. "R AY T"
            homophones.setdefault(key, []).append(word)

    return homophones





@mod.action_class
class Actions:
    def homophoner_resolve(input: str, context: str) -> str:
        """Finds the homophone candidate of input that most closely matches the semantic meaning of context"""
        print(context)
        return find_nearest_homophone(input, context)


# Load model async on talon startup
import threading
app.register("ready", lambda: threading.Thread(target=load_model, daemon=True).start())
