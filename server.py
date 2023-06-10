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
from time import sleep
from serial import Serial
from alarms import Alarms



def sunrise(value=b'\x01'):
    logging.info(f'send {value = }')
    for i in range(5):
        try:
            with Serial('ttyBT', timeout=0.1) as device:
                device.write(value)
                device.flush()
                echo = device.read()
                assert echo == value, f'incorrect {echo = }'
        except Exception as e:
            logging.error(e)
            sleep(1)
        else:
            break
    else:
        logging.error('drop alarm')


async def schedule_handler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


alarms = Alarms(sunrise)

with open('data') as data:
    for i, time in enumerate(data.read().split()):
        alarms.add(i, time)

loop = asyncio.get_event_loop()
loop.create_task(schedule_handler())
loop.run_forever()
