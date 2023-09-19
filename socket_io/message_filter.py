from words_filter.models import WordsFilter
import json


async def message_filter(message):
    blocked_words = []
    lower_message = message.lower()
    splited_message = lower_message.split()
    list_word_of_message = []
    for word in splited_message:
        word = word.replace(",", "")
        word = word.replace(".", "")
        list_word_of_message.append(word)

    blocked_words = WordsFilter.objects.get()
    if blocked_words is None:
        return blocked_words
    blocked_words = json.loads(blocked_words.key_words)

    founded_words = []
    for word in blocked_words:
        if word in list_word_of_message:
            founded_words.append(word)
    return founded_words
