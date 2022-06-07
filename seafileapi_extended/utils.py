"""Utils"""


def is_ascii(text) -> bool:
    """Check if is ascii"""
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True
