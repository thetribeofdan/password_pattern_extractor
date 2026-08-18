from tokenizer import tokenize
from classifier import classify
from pattern_builder import build_pattern
from token_reconstructor import reconstruct_tokens
from capitalization import detect_capitalization
from leet_normalizer import normalize_leet


def extract(password: str):

    tokens = tokenize(password)

    classifications = []
    numbers = []
    symbols = []
    alpha_tokens = []
    token_positions = []

    cursor = 0

    for t in tokens:

        c = classify(t)
        classifications.append(c)

        position = password.lower().find(t.lower(), cursor)

        if c == "token":

            alpha_tokens.append(t.lower())
            token_positions.append(position)

        elif c in ["year", "number", "123"]:
            numbers.append(t)

        elif c == "symbol":
            symbols.append(t)

        cursor = position + len(t)

    # normalized_tokens = reconstruct_tokens(tokens)

    pattern = build_pattern(tokens, classifications)

    capitalization = detect_capitalization(password)

    return {
        "password": password,
        # "normalized": normalize_leet(password.lower()),
        "tokens": alpha_tokens,
        # "normalized_tokens": normalized_tokens,
        "numbers": numbers,
        "symbols": symbols,
        "pattern": pattern,
        "capitalization": capitalization,
        "length": len(password),
        "token_positions": token_positions
    }
