# phony [homophone] [context word]
phony <user.word> <user.word>: insert(user.homophoner_resolve(word_1, word_2))
{user.word_formatter} <user.word> as in <user.word>: user.insert_formatted(user.homophoner_resolve(word_1, word_2), word_formatter)

customize homophoner overrides: user.homophoner_customise()
