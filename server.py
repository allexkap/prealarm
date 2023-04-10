import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=(
        logging.FileHandler('server.log'),
        logging.StreamHandler(),
    ),
)


import asyncio
import schedule
from serial import Serial


class Alarms:

    weekdays = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

    def __init__(self, func):
        self.alarms = [None] * 7
        self.func = func

    def add(self, weekday, time):
        self.remove(weekday)
        self.alarms[weekday] = eval(f'schedule.every().{Alarms.weekdays[weekday]}.at(time)').do(self.func)

    def remove(self, weekday):
        if self.alarms[weekday]:
            schedule.cancel_job(self.alarms[weekday])


def sunrise(value=b'\x01'):
    logging.info(f'send {value = }')
    try:
        with Serial('ttyBT', timeout=0.1) as device:
            device.write(value)
            device.flush()
            echo = device.read()
            assert echo == value, f'incorrect {echo = }'
    except Exception as e:
        logging.error(e)


async def schedule_handler():
    while True:
        print(schedule.idle_seconds())
        schedule.run_pending()
        await asyncio.sleep(1)


alarms = Alarms(sunrise)

with open('data') as data:
    for i, time in enumerate(data.read().split()):
        alarms.add(i, time)

loop = asyncio.get_event_loop()
loop.create_task(schedule_handler())
loop.run_forever()
