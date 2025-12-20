import collections

from src.constants import DATE_DELIMITER

Date = collections.namedtuple('Date', ('day', 'month', 'year'))

def date_tuple_to_str(date: Date, delimiter: str = DATE_DELIMITER) -> str:
    return f"{"0" + str(date[0]) if date[0] < 10 else str(date[0])}{delimiter}{"0" + str(date[1]) if date[1] < 10 else str(date[1])}{delimiter}{date[2]}"

def date_str_to_tuple(date: str) -> Date:
    day, month, year = map(int, date.split(DATE_DELIMITER))

    return day, month, year

def get_dates_between_days(first_day: int, last_day: int, month: int, year: int) -> list[Date]:
    dates = []

    for d in range(first_day, last_day + 1):
        dates.append(Date(d, month, year))

    return dates

def get_dates_between_months(first_day: int, first_month: int, last_day: int, last_month: int, year: int) -> list[Date]:
    dates = []

    month = first_month
    day1 = first_day
    day2 = 30  # TODO

    while month <= last_month:
        if month == last_month:
            day2 = last_day

        dates.extend(get_dates_between_days(day1, day2, month, year))

        month += 1

        day1 = 1
        day2 = 30

    return dates

def get_dates_between_years(first_day: int, first_month: int, first_year: int, last_day: int, last_month: int, last_year: int) -> list[Date]:
    dates = []

    year = first_year
    month1 = first_month
    month2 = 12
    day1 = first_day
    day2 = 30  # TODO

    while year <= last_year:
        if year == last_year:
            month2 = last_month
            day2 = last_day

        dates.extend(get_dates_between_months(day1, month1, day2, month2, year))

        year += 1

        month1 = 1
        month2 = 12
        day1 = 1
        day2 = 30

    return dates

def get_next_day(date: Date) -> Date:
    day = date.day + 1
    month = date.month
    year = date.year

    if day > 30: #TODO
        day = 1
        month += 1

        if month > 12:
            month = 1
            year += 1

    return Date(day, month, year)

def get_previous_day(date: Date) -> Date:
    day = date.day - 1
    month = date.month
    year = date.year

    if day < 1:
        day = 30 # TODO
        month -= 1

        if month < 1:
            month = 12
            year -= 1

    return Date(day, month, year)