"""Process one Line of the input file."""

import difflib


def get_max_diff_area(a: str, b: str, /) -> tuple[int, int]:
    """Get the maximum difference area."""
    front, back = 0, 0

    for i, j in zip(a, b):
        if i != j:
            break
        front += 1

    for i, j in zip(reversed(a[front:]), reversed(b[front:])):
        if i != j:
            break
        back -= 1

    return front, back


def get_diff(
    a: str,
    b: str,
    /,
) -> tuple[dict[tuple[int, int], str], dict[tuple[int, int], str]]:
    """Get the difference of two strings."""
    front, back = get_max_diff_area(a, b)
    a, b = a[front:back], b[front:back]
    matcher = difflib.SequenceMatcher(None, a, b)
    dict_a, dict_b = {}, {}

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        match tag:
            case "replace":
                dict_a[(i1 + front, i2 + front)] = "update"
                dict_b[(j1 + front, j2 + front)] = "update"
            case "insert":
                dict_b[(j1 + front, j2 + front)] = "insert"
            case "delete":
                dict_a[(i1 + front, i2 + front)] = "delete"
            case "equal": pass

    return dict_a, dict_b
