import utime

from src.constants import MONTHS
import src.utilities as utilities
from src.utilities import Date

class DateManager(object):
    def __init__(self):
        self.__today = None

        self.set_today()

    def get_today(self) -> Date:
        return self.__today

    def set_today(self) -> None:
        date_time = utime.localtime()

        self.__today = utilities.local_to_actual_date(date_time)

    def refresh_today(self) -> bool:
        current_date = utilities.local_to_actual_date(utime.localtime())

        if current_date != self.__today:
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