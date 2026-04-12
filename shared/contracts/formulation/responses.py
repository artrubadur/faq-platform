from pydantic import BaseModel, ConfigDict

from shared.contracts.types import Int64Id


class FormulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Int64Id
    question_id: Int64Id
    question_text: str


class FormulationsAmountResponse(BaseModel):
    amount: int
