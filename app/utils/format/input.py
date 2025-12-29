import re


def format_input(input: str, skippable: bool = False) -> str | None:
    formated = re.sub(r"\([^)]*\)", "", input).strip()
    if formated.lower() == "skip" and skippable:
        return None
    return formated
