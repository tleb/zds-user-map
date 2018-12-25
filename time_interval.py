import time
import datetime
from datetime import timedelta, datetime, MINYEAR

class TimeInterval:
    def __init__(self, interval):
        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)

        self.interval = interval
        self.last = datetime(MINYEAR, 1, 1)

    def start(self):
        # last+interval is the timedate at which we can start the action again
        diff = ((self.last + self.interval) - datetime.now()).total_seconds()

        if diff > 0:
            time.sleep(diff)

        self.last = datetime.now()
