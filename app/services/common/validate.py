from app.core.customization import messages


def validate_page(page: str):
    if not page.isdigit():
        raise ValueError(messages.validation.common.page_invalid)
    int_page = int(page)

    if int_page < 1:
        raise ValueError(messages.validation.common.page_negative)

    return int_page
