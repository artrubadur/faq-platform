import json
import traceback
from typing import Any


def serialize_json(record: dict[str, Any]) -> str:
    payload = {
        "time": int(record["time"].timestamp()),
        "level": record["level"].name,
        "message": record["message"],
        "name": record["name"],
    }
    exception = record["exception"]
    if exception:
        payload["exception"] = "".join(
            traceback.format_exception(
                exception.type, exception.value, exception.traceback
            )
        )

    repeat = record.get("_repeat", None)
    if repeat:
        payload["repeat"] = repeat

    return f"{{{json.dumps(payload, ensure_ascii=False)}}}\n"
