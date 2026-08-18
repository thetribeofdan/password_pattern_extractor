LEET_MAP = {
    "4": "a",
    "@": "a",
    "3": "e",
    "1": "i",
    "!": "i",
    "0": "o",
    "$": "s",
    "5": "s",
    "7": "t"
}


def normalize_leet(token: str):

    normalized = ""

    for char in token.lower():

        if char in LEET_MAP:
            normalized += LEET_MAP[char]
        else:
            normalized += char

    return normalized
