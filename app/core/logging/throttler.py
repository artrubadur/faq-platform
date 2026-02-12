import asyncio
from dataclasses import dataclass
from typing import Any

from app.dialogs.send.common import send_log
from app.services.notification import notify
from app.storage.models.user import Role


@dataclass
class LogEntry:
    name: str
    message: str
    level: Any
    exception: Exception | None
    repeat: int | None
    repeat_limit: int


class TelegramThrottler:
    def __init__(self, cooldown: int = 10):
        self.cooldown = cooldown
        self.queues: dict[str, asyncio.Queue[LogEntry]] = {}
        self.workers: dict[str, asyncio.Task] = {}

    async def _worker(self, name: str):
        queue = self.queues[name]
        while True:
            entry = await queue.get()
            try:
                await notify(
                    Role.ADMIN,
                    send_log,
                    entry.name,
                    entry.message,
                    entry.level,
                    entry.exception,
                    entry.repeat,
                    entry.repeat_limit,
                )
                await asyncio.sleep(self.cooldown)
            finally:
                queue.task_done()

    def add_log(
        self,
        name: str,
        message: str,
        level: Any,
        exception: Exception | None,
        repeat: int | None,
        repeat_limit: int,
    ):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        if name not in self.queues:
            self.queues[name] = asyncio.Queue()
            self.workers[name] = loop.create_task(self._worker(name))

        self.queues[name].put_nowait(
            LogEntry(name, message, level, exception, repeat, repeat_limit)
        )
