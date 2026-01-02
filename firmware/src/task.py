import utime

import src.utilities as utilities
from src.utilities import Date
from src.validator import Validator


class Task(object):
    _validator = Validator()

    def __init__(self, description: str, start_date: Date, end_date: Date, id: str = None) -> None:
        Task._validator.validate_task(description, start_date, end_date)

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
        Task._validator.validate_description(new_description)

        self.__description = new_description

    @property
    def start_date(self) -> Date:
        return self.__start_date

    @start_date.setter
    def start_date(self, new_start_date: Date) -> None:
        Task._validator.validate_dates(new_start_date, self.__end_date)

        # old_start_date = self.__start_date
        self.__start_date = new_start_date

        # return old_start_date

    @property
    def end_date(self) -> Date:
        return self.__end_date

    @end_date.setter
    def end_date(self, new_end_date: Date) -> None:
        Task._validator.validate_dates(self.__start_date, new_end_date)

        self.__end_date = new_end_date

    def get_dates(self) -> list[Date]:
        day_index = 0
        month_index = 1
        year_index = 2

        return utilities.get_dates_between_years(int(self.__start_date[day_index]), int(self.__start_date[month_index]), int(self.__start_date[year_index]),
                                                     int(self.__end_date[day_index]), int(self.__end_date[month_index]), int(self.__end_date[year_index]))

    def __str__(self) -> str:
        return self.__description

    def __repr__(self) -> str:
        return f"Task(id={self.__id}, description={self.__description}, start_date={utilities.date_tuple_to_str(self.__start_date)}, end_date={utilities.date_tuple_to_str(self.__end_date)})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Task) and self.__id == other.id

    def __hash__(self) -> hash:
        return hash(self.__id)

    def to_json(self) -> dict:
        return {"id": self.__id, "description": self.__description, "start_date": utilities.date_tuple_to_str(self.__start_date), "end_date": utilities.date_tuple_to_str(self.__end_date)}