import re

YEAR_REGEX = re.compile(r"(19\d{2}|20\d{2})")


def classify(token: str):

    if token.isalpha():
        return "token"

    if token.isdigit():

        if YEAR_REGEX.fullmatch(token):
            return "year"

        if token == "123":
            return "123"

        return "number"

    return "symbol"
