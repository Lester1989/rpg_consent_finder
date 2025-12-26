from nicegui.testing import User


def marked_elements(user: User, marker: str) -> dict[str, Any]:
    """
    Return a mapping of concatenated markers to elements.

    Args:
        user: The User instance for finding elements
        marker: The marker string to search for

    Returns:
        Dict mapping concatenated marker strings to their elements.
        Note: Elements with duplicate marker combinations will overwrite earlier entries.
    """
    return {
        "".join(element._markers): element
        for element in user.find(marker).elements
        if element._markers
    }
