"""
Used as request ID generator
"""

from string import ascii_letters
import random
from datetime import datetime

class RandomStringGenerator:
    def __init__(self, length=10):
        self.length = length

    def getNext(self):
        random.seed(str(datetime.now()))
        res = ""
        for i in range(self.length):
            res += random.choice(ascii_letters)
        return res