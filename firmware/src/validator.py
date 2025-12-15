import re

from src.constants import DATE_DELIMITER

class Validator(object):
    def validate_task(self, description: str, start_date: str, end_date: str):
        self.validate_description(description)
        self.validate_dates(start_date, end_date)

    def validate_description(self, description: str) -> None:
        if not isinstance(description, str):
            raise TypeError("Description is not string.")

    def validate_dates(self, start_date: str, end_date: str) -> None:
        self.validate_date(start_date)
        self.validate_date(end_date)

        if not self.check_dates_comparison(start_date, end_date):
            raise ValueError("Start day should be before the end day.")

    def validate_date(self, date: str):
        if not self.check_date_type(date):
            raise TypeError(f"{date} is not string.")

        if not self.check_date_format(date):
            raise ValueError(f"{date} does not have format <day>{DATE_DELIMITER}<month>{DATE_DELIMITER}<year>.")

    # ---

    def check_date_type(self, date: str) -> bool:
        if not isinstance(date, str):
            return False

        return True

    def check_date_format(self, date: str) -> bool:
        pattern = re.compile(f"^[0-3][0-9]{DATE_DELIMITER}[0-9]{DATE_DELIMITER}20[0-3][0-9]$")

        if pattern.match(date):
            return True

        return False

    def check_dates_comparison(self, start_date: str, end_date: str) -> bool:
        start_date_args = start_date.split(DATE_DELIMITER)
        end_date_args = end_date.split(DATE_DELIMITER)

        start_date_day = int(start_date_args[0])
        start_date_month = int(start_date_args[1])
        start_date_year = int(start_date_args[2])

        end_date_day = int(end_date_args[0])
        end_date_month = int(end_date_args[1])
        end_date_year = int(end_date_args[2])

        if  start_date_year < end_date_year:
            return True
        elif start_date_year == end_date_year:
            if start_date_month < end_date_month:
                return True
            elif start_date_month == end_date_month:
                if start_date_day <= end_date_day:
                    return True

        return False