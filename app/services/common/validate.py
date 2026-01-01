def validate_page(page: str | int):
    page = validate_int(page)
    if page < 1:
        raise ValueError("Page cannot be less than one")

    return page


def validate_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    if number.isdigit():
        return int(number)

    raise ValueError("ID is incorrect")
