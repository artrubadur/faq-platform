from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from shared.contracts.types import Int64Id

FormulationFields = Literal["id", "question_id", "question_text"]


class CreateFormulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: Int64Id
    question_text: str


class UpdateFormulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: Int64Id | None = None
    question_text: str | None = None
    recompute_embedding: bool | None = None


class ListFormulationsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    order_by: FormulationFields
    ascending: bool
    question_id: Int64Id | None = None
