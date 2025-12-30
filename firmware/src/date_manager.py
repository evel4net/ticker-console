import utime

from src.config_private import UTC_OFFSET
from src.constants import MONTHS
import src.utilities as utilities
from src.utilities import Date

class DateManager(object):
    def __init__(self):
        self.__today = None

        self.__last_update_time = None
        self.__delay_until_midnight = None

        self.set_today()

    def get_today(self) -> Date:
        return self.__today

    def set_today(self) -> None:
        date_time = utime.localtime()

        self.__today = Date(date_time[2], date_time[1], date_time[0])

        self.__last_update_time = utime.time()
        self.__delay_until_midnight = utilities.get_seconds_until_midnight(date_time[3] + UTC_OFFSET, date_time[4], date_time[5])

    def refresh_today(self) -> bool:
        current_time = utime.time()

        if current_time - self.__last_update_time >= self.__delay_until_midnight:
            self.set_today()

            return True

        return False

    def get_current_month(self) -> str:
        return MONTHS[int(self.__today.month)]

    def get_number_days_in_current_month(self) -> int:
        return utilities.get_number_days_in_month(self.__today.month, self.__today.year)

    def get_week_day_of_current_month(self, day: int) -> int:
        week_day_date_time = utime.mktime((self.__today.year, self.__today.month, day, 0, 0, 0, 0, 0))

        return utime.localtime(week_day_date_time)[6]