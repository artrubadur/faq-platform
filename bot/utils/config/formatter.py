from string import Formatter

_RUNTIME_TEMPLATE_FIELDS = [
    "identity",
    "id",
    "user",
    "first_name",
    "last_name",
    "username",
    "full_name",
    "date",
    "user_link",
    "user_role",
    "question",
    "question_text",
    "answer_text",
    "rating",
    "old",
    "new",
    "page",
    "max_page",
    "content",
    "exception",
]


class SafeFormatter(Formatter):
    def __init__(self, allowed_extra: list[str] = _RUNTIME_TEMPLATE_FIELDS):
        super().__init__()
        self.allowed_extra = allowed_extra

    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, AttributeError) as exc:
            if key not in self.allowed_extra:
                raise ValueError(
                    f"Attempt to access a non-existent field: {key}"
                ) from exc
            return "{" + str(key) + "}"
