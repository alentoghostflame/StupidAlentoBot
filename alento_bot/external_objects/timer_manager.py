from datetime import datetime
from typing import Dict, Optional, Coroutine, Hashable
import logging


logger = logging.getLogger("main_bot")


class TimerData:
    def __init__(self, time: datetime, coroutine: Coroutine):
        self.time: datetime = time
        self.coroutine: Coroutine = coroutine


class TimerManager:
    def __init__(self):
        self._timer_storage: Dict[Hashable, TimerData] = dict()

    def add_timer(self, uuid: Hashable, time: datetime, coroutine: Coroutine):
        if uuid in self._timer_storage:
            raise ValueError(f"Tried to add a timer, but UUID {uuid} was already there!")
        else:
            self._timer_storage[uuid] = TimerData(time, coroutine)

    def get_timer(self, uuid: Hashable) -> Optional[TimerData]:
        return self._timer_storage.get(uuid, None)

    def rm_timer(self, uuid: Hashable) -> Optional[TimerData]:
        return self._timer_storage.pop(uuid, None)

    async def tick(self):
        time_now = datetime.utcnow()
        for key, value in self._timer_storage.copy().items():
            if value.time < time_now:
                self._timer_storage.pop(key)
                await value.coroutine
