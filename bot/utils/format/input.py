import re


def format_input(input: str) -> str:
    return re.sub(r"\([^)]*\)", "", input).strip()
