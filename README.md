Say goodbye to the homophone selection menu! Instead of `phones right` [wait for menu] `choose two`, simply say `phony right read` and talon will output "write"

## Installation

Installed the dependencies to the talon pip environment. On Linux or mac this is done like `~/.talon/bin/pip install gensim nltk`

When the command is used for the first time in a given talon session, it will load and possibly download the model that it needs. This will freeze talon for a minute, so be wary

## Usage/how it works

` phony [homophone] [context word]` - Simply say this, where the context word is a word that is related in meaning to the homophone you are trying to select. For example, for the homophone two, you might use number.

It does this by using a small local word vector model, which models the semantic nearness of words.
It compares each of the possible homophones of your homophone target word, and selects the one that is closest to your context word.

Homophone candidates are pulled from the standard talon-community homophone list, but if none are available it will try to calculate homophones using phoneme similarity (meaning it is much more flexible than the usual community homophones).

## Caveats

* The script tries to load the language model asynchronously win talon loads, but there will be a slight delay when you first start up talon until it is fully functional. (This seems to also include briefly freezing talon on its startup, but doesn't seem to freeze it fully. This usually is only 30 seconds to a minute, but will be slower the very first time when it actually downloads a new model)
* What the models perceive as a similar context word might differ from what we would intuit. For example, `glove-wiki-gigaword-50` sees read as more similar to right than write, so "right read" will give you "right".

## Downloading Word Embedding Models

This script will try and download and load the models on talon startup. Sometimes this will fail with an SSL/certificate error because talon sometimes interferes with certificates that block the model download.
If you experience this issue, to download the word embedding models used by Homophoner, you must run the `download_model.py` script using your system Python interpreter, not from within Talon.

Before running the script, ensure you have installed the required dependency (in a non talon python this time):

```bash
pip install gensim
```

Then run the script from the command line:

```bash
python download_model.py [model_name]
```

If no model name is provided, the default model `glove-wiki-gigaword-50` will be loaded.
