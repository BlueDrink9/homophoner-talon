Say goodbye to the homophone selection menu! Instead of `phones right` [wait for menu] `choose two`, simply say `phony right read` and talon will output "write"

## Installation

Installed the dependencies to the talon pip environment. On Linux or mac this is done like `~/.talon/bin/pip install gensim`

When the command is used for the first time in a given talon session, it will load and possibly download the model that it needs. This will freeze talon for a minute, so be wary

## Usage/how it works

` phony [homophone] [context word]` - Simply say this, where the context word is a word that is related in meaning to the homophone you are trying to select. For example, for the homophone two, you might use number.

It does this by using a small local word vector model, which models the semantic nearness of words.
It compares each of the possible homophones of your homophone target word, and selects the one that is closest to your context word.

Homophone candidates are pulled from the standard talon-community homophone list, but if none are available it will try to calculate homophones using phoneme similarity (meaning it is much more flexible than the usual community homophones).
