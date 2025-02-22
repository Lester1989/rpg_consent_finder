import string


def sanitize_name(name: str) -> str:
    return "".join(
        c if c in string.ascii_letters + string.digits + "_-" else "-" for c in name
    ).lower()
