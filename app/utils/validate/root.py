def validate_path(path: str | None) -> str:
    if path is None:
        raise ValueError("The path is not set")
    return path
