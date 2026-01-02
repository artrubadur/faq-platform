def validate_page(page: str):
    if not page.isdigit():
        raise ValueError("Page is invalid")
    int_page = int(page)
    
    if int_page < 1:
        raise ValueError("Page cannot be less than one")

    return int_page
