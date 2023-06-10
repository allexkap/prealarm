import schedule
import re


class Alarms:

    weekdays = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')

    def __init__(self, func, delay=30*60):
        self.alarms = [None] * 7
        self.func = func
        self.delay = delay

    @classmethod
    def dayof(cls, job, weekday):
        job.start_day = cls.weekdays[weekday]
        return job

    def add(self, weekday, time):
        try:
            h, m = map(int, re.match(r'(\d{1,2})[ .:](\d{1,2})$', time).groups())
        except AttributeError:
            raise ValueError(f'time data {time} does not match format \'HH:MM\'')
        s = ((h * 60) + m) * 60 - self.delay
        time = f'{s//3600%24:02}:{s//60%60:02}:{s%60:02}'
        self.remove(weekday)
        self.alarms[weekday] = self.dayof(schedule.every().week, weekday - (s<0)).at(time).do(self.func)

    def remove(self, weekday):
        if self.alarms[weekday]:
            schedule.cancel_job(self.alarms[weekday])
        self.alarms[weekday] = None
