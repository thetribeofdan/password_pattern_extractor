def build_pattern(tokens, classifications):

    pattern_parts = []

    for c in classifications:
        pattern_parts.append(f"{{{c}}}")

    return "".join(pattern_parts)
