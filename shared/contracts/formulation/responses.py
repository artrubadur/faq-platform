from pydantic import BaseModel, ConfigDict


class FormulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    question_text: str


class FormulationsAmountResponse(BaseModel):
    amount: int
