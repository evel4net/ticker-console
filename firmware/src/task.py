import utime

from src.constants import DATE_DELIMITER
import src.utilities as utilities

class Task(object):
    def __init__(self, description: str, start_date: str, end_date: str, id: str = None): # TODO validate params here or outside?
        if id is None:
            id = self.__generate_id()

        self.__id = id

        self.__description = description
        self.__start_date = start_date
        self.__end_date = end_date

    def __generate_id(self) -> str:
        return str(utime.ticks_us())

    @property
    def id(self) -> str:
        return self.__id

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, new_description: str) -> None:
        self.__description = new_description

    @property
    def start_date(self) -> str:
        return self.__start_date

    @start_date.setter
    def start_date(self, new_start_date: str) -> None:
        self.__start_date = new_start_date

    @property
    def end_date(self) -> str:
        return self.__end_date

    @end_date.setter
    def end_date(self, new_end_date: str) -> None:
        self.__end_date = new_end_date

    def get_dates(self) -> list[str]:
        # dates = [self.__start_date]

        # if self.__end_date != self.__start_date:
        start_date_args = self.__start_date.split(DATE_DELIMITER)
        end_date_args = self.__end_date.split(DATE_DELIMITER)

        day_index = 0
        month_index = 1
        year_index = 2

        return utilities.get_dates_between_years(int(start_date_args[day_index]), int(start_date_args[month_index]), int(start_date_args[year_index]),
                                                     int(end_date_args[day_index]), int(end_date_args[month_index]), int(end_date_args[year_index]))

        # return dates

    def __str__(self) -> str:
        return self.__description

    def __repr__(self) -> str:
        return f"Task(id={self.__id}, description={self.__description}, start_date={self.__start_date}, end_date={self.__end_date})"

    def __eq__(self, other):
        return isinstance(other, Task) and self.__id == other.id

    def __hash__(self):
        return hash(self.__id)

    def to_json(self):
        return {"id": self.__id, "description": self.__description, "start_date": self.__start_date, "end_date": self.__end_date}