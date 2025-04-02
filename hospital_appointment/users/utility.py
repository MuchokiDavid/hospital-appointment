import uuid

def generate_unique_id() -> str:
    """
    Generate a unique ID.

    This function creates a universally unique identifier (UUID) using Python's uuid module.
    The generated ID is guaranteed to be unique across all possible invocations.

    Returns:
        str: A string representation of the generated UUID.

    Example:
        >>> generate_unique_id()
        '123e4567-e89b-12d3-a456-426614174000'
    """
    return str(uuid.uuid4())