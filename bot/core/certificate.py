from pathlib import Path

from aiogram.types import FSInputFile

_CERTIFICATE_PATH = Path("config/webhook.pem")

certificate: FSInputFile | None = None

status = "Failed to check the status of webhook certificate"
if not _CERTIFICATE_PATH.exists() or not _CERTIFICATE_PATH.is_file():
    status = (
        "No webhook certificate loaded: "
        f"File {str(_CERTIFICATE_PATH)} does not exist."
    )
else:
    certificate = FSInputFile(path=str(_CERTIFICATE_PATH))
    status = "Webhook certificate has been loaded from " f"{str(_CERTIFICATE_PATH)}"
