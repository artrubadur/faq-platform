from string import Formatter


class SafeFormatter(Formatter):
    def __init__(self, allowed_extra: list[str] = []):
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
