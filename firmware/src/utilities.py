from src.constants import DATE_DELIMITER

def ints_to_date(day: int, month: int, year: int):
    return f"{"0" + str(day) if day < 10 else str(day)}{DATE_DELIMITER}{"0" + str(month) if month < 10 else str(month)}{DATE_DELIMITER}{year}"

def pretty_format_date(date: str, new_delimiter: str) -> str:
    return date.replace(DATE_DELIMITER, new_delimiter)

def get_dates_between_days(first_day, last_day, month, year):
    dates = []

    for d in range(first_day, last_day + 1):
        dates.append(ints_to_date(d, month, year))

    return dates

def get_dates_between_months(first_day, first_month, last_day, last_month, year):
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

def get_dates_between_years(first_day, first_month, first_year, last_day, last_month, last_year):
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

def get_next_day(date: str) -> str:
    date_args = date.split(DATE_DELIMITER)
    day = int(date_args[0]) + 1
    month = int(date_args[1])
    year = int(date_args[2])
    if day > 30: #TODO
        day = 1
        month += 1

        if month > 12:
            month = 1
            year += 1

    return ints_to_date(day, month, year)

def get_previous_day( date: str) -> str:
    date_args = date.split(DATE_DELIMITER)
    day = int(date_args[0]) - 1
    month = int(date_args[1])
    year = int(date_args[2])

    if day < 1:
        day = 30 # TODO
        month -= 1

        if month < 1:
            month = 12
            year -= 1

    return ints_to_date(day, month, year)