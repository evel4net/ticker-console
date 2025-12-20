import json
import os
import urequests
import utime

from src.constants import DATE_DELIMITER, MONTHS
from src.config_private import LATITUDE, LONGITUDE, TIMEZONE
from src.task import Task
from src.day import Day

class Repository(object):
    def __init__(self):
        self.__days_path = "./logs/days"
        self.__tasks_path = "./logs/tasks"
        self.__errors_file_path = './logs/errors.txt'

        self.__days = {} # date: Day
        self.__tasks = {} # task_id: Task

        self.__today = "06_12_2025"

        self.__weather_api_url = self.__get_weather_api_url()

        self.load_data()
        # self.mockup_data()
        # print(self.__tasks)
        # print(self.__days)
        # print("\n")

        # print(self.get_today())
        # print(self.get_weekday())
        # print(self.get_current_month())
        # print(self.get_current_month_first_weekday())

    def mockup_data(self):
        self.add_task(Task("citit", "06_12_2025", "07_12_2025"))
        self.add_task(Task("cumparaturi Craciun", "07_12_2025", "07_12_2025"))
        self.add_task(Task("invatat examen practic", "06_12_2025", "06_12_2025"))
        self.add_task(Task("scris proiect facultate", "06_12_2025", "08_12_2025"))
        self.add_task(Task("curatenie apartament", "07_12_2025", "07_12_2025"))
        self.add_task(Task("vizita la bunici", "08_12_2025", "08_12_2025"))
        self.add_task(Task("programare sala sport", "08_12_2025", "09_12_2025"))
        self.add_task(Task("gatit cina speciala", "09_12_2025", "09_12_2025"))
        self.add_task(Task("pregatire prezentare", "09_12_2025", "10_12_2025"))
        self.add_task(Task("plimbare in parc", "10_12_2025", "10_12_2025"))
        self.add_task(Task("pregatire proiect mare", "06_12_2025", "10_12_2025"))
        self.add_task(Task("organizare eveniment facultate", "06_12_2025", "10_12_2025"))
        self.add_task(Task("studii pentru examen final", "06_12_2025", "10_12_2025"))

    def load_data(self):
        for filename in os.listdir(self.__days_path):
            filepath = self.__days_path + "/" + filename

            with open(filepath, 'r') as f:
                day = json.load(f)

                date = day["date"]
                tasks = day["task_ids"]
                status = day["is_finished_status"]

                self.__days[date] = Day(date, tasks, status)

        for filename in os.listdir(self.__tasks_path):
            filepath = self.__tasks_path + "/" + filename

            with open(filepath, 'r') as f:
                task = json.load(f)

                id = task["id"]
                description = task["description"]
                start_date = task["start_date"]
                end_date = task["end_date"]

                self.__tasks[id] = Task(description, start_date, end_date, id)

    def save_day(self, day: Day) -> None:
        filepath = self.__days_path + "/" + day.date + ".json"

        with open(filepath, 'w') as f:
            json.dump(day.to_json(), f, separators=(',', ':'))

    def save_task(self, task: Task) -> None:
        filepath = self.__tasks_path + "/" + task.id + ".json"

        with open(filepath, 'w') as f:
            json.dump(task.to_json(), f, separators=(',', ':'))

    def save_error(self, error: str) -> None:
        with open(self.__errors_file_path, 'a') as f:
            f.write('\n' + error)

    def get_all_days(self) -> dict[str, Day]:
        return self.__days

    def get_all_tasks(self) -> dict[str, Task]:
        return self.__tasks

    def get_unfinished_tasks_by_day(self, date: str) -> list[tuple[Task, bool]]:
        tasks = []

        if date in self.__days.keys():
            tasks = [(self.__tasks[task_id], False) for task_id in self.__days[date].unfinished_task_ids]

        return tasks

    def get_all_tasks_by_day(self, date: str) -> list[tuple[Task, bool]]:
        tasks = []

        if date in self.__days.keys():
            tasks = [(self.__tasks[task_id], is_finished) for task_id, is_finished in self.__days[date].tasks]

        return tasks

    def get_day(self, date: str) -> Day:
        return self.__days[date]

    def get_task(self, task_id: str) -> Task:
        return self.__tasks[task_id]

    def get_task_by_index(self, date: str, index: int) -> Task:
        return self.__tasks[self.__days[date].get_task_id_by_index(index)]

    def get_task_id_by_index(self, date: str, index: int) -> str:
        return self.__days[date].get_task_id_by_index(index)

    def get_count_tasks(self, date: str) -> int:
        return self.__days[date].get_count_tasks()

    def add_day(self, day: Day) -> None:
        self.__days[day.date] = day

        self.save_day(day)

    def add_task(self, task: Task) -> None:
        self.__tasks[task.id] = task

        for date in task.get_dates():
            if date in self.__days.keys():
                day = self.__days[date]
                day.add_task(task.id)

                self.save_day(day)
            else:
                self.add_day(Day(date, [task.id], [False]))

        self.save_task(task)

    def is_task_finished(self, date: str, index: int) -> bool:
        return self.__days[date].is_task_finished(index)

    def set_task_finished(self, date: str, index: int) -> None:
        day = self.__days[date]
        day.set_task_finished(index)

        self.save_day(day)

        # print(self.__days)

    # --- API

    def __get_weather_api_url(self) -> str:
        api_url = "https://api.open-meteo.com/v1/forecast"

        parameters = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,precipitation_probability,weather_code",
            "timezone": TIMEZONE,
            "forecast_days": 1,
        }

        request_url = api_url + "?"
        for k, v in parameters.items():
            request_url += f"{str(k)}={str(v)}&"

        return request_url[:-1]

    def get_weather(self) -> (float, int, int):
        response = urequests.get(self.__weather_api_url)

        data = response.json()

        response.close()

        temperature = data['current']['temperature_2m']
        precipitation = data['current']['precipitation_probability']
        weather_code = data['current']['weather_code']

        print(f"Temperature = {temperature} C, Precipitation = {precipitation}%, Weather Code = {weather_code}")

        return (temperature, precipitation, weather_code)

    # --- DATE TIME

    def get_current_month(self) -> str:
        return MONTHS[int(self.__today.split(DATE_DELIMITER)[1])]

    def set_today(self):
        date_time = utime.localtime()

        self.__today = f"{date_time[2]}{DATE_DELIMITER}{date_time[1]}{DATE_DELIMITER}{date_time[0]}"

    def get_today(self) -> str:
        # return str(self.__today)
        return self.__today

    def get_total_number_days_in_current_month(self) -> int:
        max_days = 31
        current_date_time = utime.localtime()
        date_time = utime.mktime((current_date_time[0], current_date_time[1], max_days, 0, 0, 0, 0, 0))
        new_date_time = utime.localtime(date_time)

        if new_date_time[1] != current_date_time[1]:
            max_days -= new_date_time[2]

        return max_days

    def get_week_day_of_current_month(self, day: int) -> int:
        data = self.__today.split(DATE_DELIMITER)

        week_day_date_time = utime.mktime((int(data[2]), int(data[1]), day, 0, 0, 0, 0, 0))
        date_time = utime.localtime(week_day_date_time)

        return date_time[6]