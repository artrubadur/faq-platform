from app.storage.models.question import Question


class AppError(Exception):
    def __init__(self, message: str, should_notify: bool = True):
        super().__init__(message)
        self.should_notify = should_notify


class SimilarityError(AppError):
    def __init__(
        self,
        message: str,
        question: Question,
        similarity: float,
        should_notify: bool = True,
    ):
        super().__init__(message, should_notify)
        self.question = question
        self.similarity = similarity


class YandexAPIError(AppError):
    def __init__(self, message: str, should_notify: bool = True):
        super().__init__(message, should_notify)
