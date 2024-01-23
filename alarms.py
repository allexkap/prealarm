import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Callable


class Alarms:
    def __init__(self, handler: Callable, delay=timedelta(minutes=30)) -> None:
        self.alarms = dict()
        self.handler = handler
        self.delay = delay

    def __setitem__(self, day: int, time: str) -> None:
        res = re.match(r'(\d{1,2})[ .:](\d\d)$', time)
        if not res or day < 0 or day > 6:
            raise ValueError
        h, m = map(int, res.groups())

        now = datetime.now()
        dtime = now.replace(hour=h, minute=m, second=0, microsecond=0)
        dtime -= self.delay

        dtime += timedelta(days=(day - now.isoweekday()) % 7)
        if dtime < now:
            dtime += timedelta(weeks=1)
        self.alarms[day] = dtime

    def __getitem__(self, day: int) -> str:
        dtime = self.alarms[day] + self.delay
        return dtime.strftime('%H.%M')

    def __iter__(self):
        yield from self.alarms

    async def __call__(self) -> None:
        while True:
            now = datetime.now()
            for day in self.alarms:
                if now > self.alarms[day]:
                    self.alarms[day] += timedelta(weeks=1)
                    self.handler()
            await asyncio.sleep(1)

    def dump(self) -> str:
        return json.dumps({key: self[key] for key in self.alarms})

    def load(self, data: str) -> None:
        self.alarms.clear()
        for k, v in json.loads(data).items():
            self[int(k)] = v
