from src.utilities import Date

class Validator(object):
    def validate_task(self, description: str, start_date: Date, end_date: Date) -> None:
        self.validate_description(description)
        self.validate_dates(start_date, end_date)

    def validate_description(self, description: str) -> None:
        if not isinstance(description, str):
            raise TypeError("Description is not string.")

    def validate_dates(self, start_date: Date, end_date: Date) -> None:
        self.validate_date(start_date)
        self.validate_date(end_date)

        if not self.check_dates_comparison(start_date, end_date):
            raise ValueError("Start day should be before the end day.")

    def validate_date(self, date: Date) -> None:
        if not self.check_date_type(date):
            raise TypeError(f"{date} is not date.")

    # ---

    def check_date_type(self, date: Date) -> bool:
        if not (isinstance(date, Date) and isinstance(date.day, int) and isinstance(date.month, int) and isinstance(date.year, int)):
            return False

        return True

    def check_dates_comparison(self, start_date: Date, end_date: Date) -> bool:
        start_date_day = start_date.day
        start_date_month = start_date.month
        start_date_year = start_date.year

        end_date_day = end_date.day
        end_date_month = end_date.month
        end_date_year = end_date.year

        if  start_date_year < end_date_year:
            return True
        elif start_date_year == end_date_year:
            if start_date_month < end_date_month:
                return True
            elif start_date_month == end_date_month:
                if start_date_day <= end_date_day:
                    return True

        return False