from leet_normalizer import normalize_leet


def reconstruct_tokens(tokens):

    """
    Rebuild meaningful word tokens
    by merging alpha fragments and
    applying leetspeak normalization.
    """

    reconstructed = []
    buffer = ""

    for token in tokens:

        # alphabetic segments
        if token.isalpha():
            buffer += token.lower()

        # leetspeak numbers inside words
        elif token.isdigit() and len(token) == 1:
            buffer += normalize_leet(token)

        else:
            if buffer:
                reconstructed.append(buffer)
                buffer = ""

    if buffer:
        reconstructed.append(buffer)

    return reconstructed
