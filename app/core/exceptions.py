from app.storage.db.models.question import Question


class SimilarityError(Exception):
    def __init__(self, message: str, question: Question):
        super().__init__(message)
        self.question = question
