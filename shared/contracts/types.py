from typing import Annotated

from pydantic import Field

INT64_MAX = 2**63 - 1
Int64Id = Annotated[int, Field(ge=1, le=INT64_MAX)]
