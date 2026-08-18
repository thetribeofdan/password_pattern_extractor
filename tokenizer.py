import re

TOKEN_REGEX = re.compile(r"[a-zA-Z]+|\d+|[^a-zA-Z\d]")


def tokenize(password: str):
    """
    Split password into tokens:
    letters, numbers, symbols
    """
    return TOKEN_REGEX.findall(password)
