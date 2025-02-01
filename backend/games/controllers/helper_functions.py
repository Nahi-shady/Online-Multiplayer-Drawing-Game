import random

from .word_pool import EASY_WORDS, HARD_WORDS, FUN

async def get_word_choices():
    word_1 = random.choice(EASY_WORDS)
    word_2 = random.choice(HARD_WORDS)
    word_3 = random.choice(FUN)
    
    while word_3.lower() == word_2.lower():
        word_2 = random.choice(HARD_WORDS)
    
    return [word_1, word_2, word_3]
