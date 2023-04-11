from datetime import datetime, timedelta
import schedule


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

    def shift(self, weekday, time):
        time = datetime.strptime(time, '%H:%M')    # except
        time = timedelta(hours=time.hour, minutes=time.minute)
        time -= timedelta(seconds=self.delay)
        if time < timedelta():
            time += timedelta(days=1)
            weekday = (weekday - 1) % 7
        time = str(time)[:-3]
        return self.dayof(schedule.every().week, weekday).at(self.shift(time)).do(self.func)

    def add(self, weekday, time):
        self.remove(weekday)
        self.alarms[weekday] = self.shift(weekday, time)

    def remove(self, weekday):
        if self.alarms[weekday]:
            schedule.cancel_job(self.alarms[weekday])
        self.alarms[weekday] = None


def task():
    pass

alarms = Alarms(task)

alarms.add(0, '12:32')
