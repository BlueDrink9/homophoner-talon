import gensim.downloader as api
import sys

DEFAULT_MODEL = "glove-wiki-gigaword-50"

def load_model(model_name: str | None = DEFAULT_MODEL):
    """Load the embedding model once and memoize it."""
    print("Homophoner is downloading/loading word model, this might take a while")
    api.load(model_name)
    import nltk
    nltk.download('cmudict')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python download_model.py [model_name]")
        print("If no model_name is provided, the default model 'glove-wiki-gigaword-50' will be loaded.")
        sys.exit(0)
    model_to_load = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    model = load_model(model_to_load)
    print(f"Model '{model_to_load}' loaded successfully.")
