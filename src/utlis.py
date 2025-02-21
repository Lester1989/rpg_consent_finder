import string


def sanitize_name(name: str) -> str:
    return "".join(
        c for c in name if c in string.ascii_letters + string.digits + "_-"
    ).lower()
