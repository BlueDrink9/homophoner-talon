Resolve homophones on the fly. Say goodbye to the homophone selection menu! Instead of `phones right` [wait for menu] `choose two`, simply say `phony right read` and talon will output "write".

## Installation

Install the dependencies (mainly `gensim`, optionally `nltk`) to the talon pip environment. On Linux or mac this is done like `~/.talon/bin/pip install gensim nltk`

* By default this depends on the community homophones dictionary. If you are not using community, define an empty function `actions.user.homophones_get(input_word)` that returns `None`.

## Usage/how it works

### Inputting a single homophone as a command

`phony [homophone] [context word]` - Simply say this, where the context word is a word that is related in meaning to the homophone you are trying to select. For example, for the homophone two, you might use number.

Assuming you are using community, you can also use word formatters with the homophone, like this:
`word there as in possession` will output "their", or `proud there as in possession` will output "Their".

### Usage in phrases or dictation mode

This is to be determined once I have liaised with the community maintainers


### Settings and configuration

There are two main settings for customization:

- `user.homophoner_model_name`: The name of the word embedding model to use (see homophoner.py for defaults and options).
- `user.homophoner_override_file`: The path to the CSV file for manual homophone/context overrides.

To edit the override file, say `customize homophoner overrides` (this command will open the CSV for editing in your text editor).

The overrides file maps a specific (input word, context) pair to a replacement homophone of your choice. Each row of the CSV uses three columns:

```
input_homophone,context_words,correct_replacement_homophone
right,read,write
```

You can add more overrides by editing this file and saving it. Newly added (input, context) pairs will be used automatically for future homophone resolution.

It does this by using a small local word vector model, which models the semantic nearness of words.
It compares each of the possible homophones of your homophone target word, and selects the one that is closest to your context word.

Homophone candidates are pulled from the standard talon-community homophone list, but if none are available it will try to calculate homophones using phoneme similarity (meaning it is much more flexible than the usual community homophones).

## Caveats

* The script tries to load the language model asynchronously win talon loads, but there will be a slight delay when you first start up talon until it is fully functional. (This seems to also include briefly freezing talon on its startup, but doesn't seem to freeze it fully. This usually is only 30 seconds to a minute, but will be slower the very first time when it actually downloads a new model)
    * If you are using this somewhere you do not have internet access, you can download the gensim model on a different machine and move it to the local folder. See the [documentation for gensim](https://radimrehurek.com/gensim/downloader.html) to see where this should live.
* What the models perceive as a similar context word might differ from what we would intuit. For example, `glove-wiki-gigaword-50` sees read as more similar to right than write, so "right read" will give you "right".
    * To work around this, there is a file that defines manual overrides for certain context words. "right read -> write" is defined already.

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
