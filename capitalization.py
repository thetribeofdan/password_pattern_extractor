def detect_capitalization(password):

    positions = []
    letters = []

    for i, c in enumerate(password):
        if c.isupper():
            positions.append(i)
            letters.append(c)

    if not positions:
        cap_type = "none"

    elif password.isupper():
        cap_type = "all_caps"

    elif positions == [0]:
        cap_type = "first_letter"

    elif len(positions) > 1:
        cap_type = "multi_capital"

    else:
        cap_type = "mixed_case"

    return {
        "positions": positions,
        "letters": letters,
        "type": cap_type
    }