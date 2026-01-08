import json
import os

from src.task import Task
from src.day import Day
import src.utilities as utilities
from src.utilities import Date
from src.constants import LOG_DAY_PATH, LOG_TASK_PATH, LOG_ERROR_PATH

class Repository(object):
    def __init__(self) -> None:
        self.__days = {} # Date(day, month, year): Day
        self.__tasks = {} # task_id: Task

        self.load_data()
        # self.dummy_data()

    def dummy_data(self) -> None:
        day = 1
        month = 1
        year = 2026

        self.add_task(Task("citit", Date(day, month, year), Date(day, month, year)))
        self.add_task(Task("cumparaturi Craciun", Date(day + 1, month, year), Date(day + 1, month, year)))
        self.add_task(Task("invatat examen practic", Date(day, month, year), Date(day, month, year)))
        self.add_task(Task("scris proiect facultate", Date(day, month, year), Date(day + 2, month, year)))
        self.add_task(Task("curatenie apartament", Date(day + 1, month, year), Date(day + 1, month, year)))
        self.add_task(Task("vizita la bunici", Date(day + 2, month, year), Date(day + 2, month, year)))
        self.add_task(Task("programare sala sport", Date(day + 2, month, year), Date(day + 3, month, year)))
        self.add_task(Task("gatit cina speciala", Date(day + 3, month, year), Date(day + 3, month, year)))
        self.add_task(Task("pregatire prezentare", Date(day + 3, month, year), Date(day + 4, month, year)))
        self.add_task(Task("plimbare in parc", Date(day + 4, month, year), Date(day + 4, month, year)))
        self.add_task(Task("pregatire proiect mare", Date(day, month, year), Date(day + 4, month, year)))
        self.add_task(Task("organizare eveniment facultate", Date(day, month, year), Date(day + 4, month, year)))
        self.add_task(Task("studii pentru examen final", Date(day, month, year), Date(day + 4, month, year)))

    def load_data(self) -> None:
        for filename in os.listdir(LOG_DAY_PATH):
            filepath = LOG_DAY_PATH + "/" + filename

            with open(filepath, 'r') as f:
                day = json.load(f)

                date = day["date"]
                tasks = day["task_ids"]
                status = day["is_finished_status"]

                self.__days[utilities.date_str_to_tuple(date)] = Day(utilities.date_str_to_tuple(date), tasks, status)

        for filename in os.listdir(LOG_TASK_PATH):
            filepath = LOG_TASK_PATH + "/" + filename

            with open(filepath, 'r') as f:
                task = json.load(f)

                id = task["id"]
                description = task["description"]
                start_date = task["start_date"]
                end_date = task["end_date"]

                self.__tasks[id] = Task(description, utilities.date_str_to_tuple(start_date), utilities.date_str_to_tuple(end_date), id)

    def save_day(self, day: Day) -> None:
        filepath = LOG_DAY_PATH + "/" + utilities.date_tuple_to_str(day.date) + ".json"

        with open(filepath, 'w') as f:
            json.dump(day.to_json(), f, separators=(',', ':'))

    def save_task(self, task: Task) -> None:
        filepath = LOG_TASK_PATH + "/" + task.id + ".json"

        with open(filepath, 'w') as f:
            json.dump(task.to_json(), f, separators=(',', ':'))

    def save_error(self, error: str) -> None:
        with open(LOG_ERROR_PATH, 'a') as f:
            f.write('\n' + error)

    def get_all_days(self) -> dict[str, Day]:
        return self.__days

    def get_all_tasks(self) -> dict[str, Task]:
        return self.__tasks

    def get_unfinished_tasks_by_day(self, date: Date) -> list[tuple[Task, bool]]:
        tasks = []

        if date in self.__days.keys():
            tasks = [(self.__tasks[task_id], False) for task_id in self.__days[date].unfinished_task_ids]

        return tasks

    def get_all_tasks_by_day(self, date: Date) -> list[tuple[Task, bool]]:
        tasks = []

        if date in self.__days.keys():
            tasks = [(self.__tasks[task_id], is_finished) for task_id, is_finished in self.__days[date].tasks]

        return tasks

    def get_day(self, date: Date) -> Day:
        return self.__days[date]

    def get_task(self, task_id: str) -> Task:
        return self.__tasks[task_id]

    def get_task_by_index(self, date: Date, index: int) -> Task:
        return self.__tasks[self.__days[date].get_task_id_by_index(index)]

    def get_task_id_by_index(self, date: Date, index: int) -> str:
        return self.__days[date].get_task_id_by_index(index)

    def get_count_tasks(self, date: Date) -> int:
        return self.__days[date].get_count_tasks()

    def add_day(self, day: Day) -> None:
        self.__days[day.date] = day

        self.save_day(day)

    def add_task(self, task: Task) -> None:
        self.__tasks[task.id] = task

        for date in task.get_dates():
            self.add_task_to_date(task.id, date)

        self.save_task(task)

    def add_task_to_date(self, task_id: str, date: Date):
        if date in self.__days.keys():
            day = self.__days[date]
            day.add_task(task_id)

            self.save_day(day)
        else:
            self.add_day(Day(date, [task_id], [False]))


    def is_task_finished(self, date: Date, index: int) -> bool:
        return self.__days[date].is_task_finished(index)

    def set_task_finished(self, date: Date, index: int) -> None:
        day = self.__days[date]
        day.set_task_finished(index)

        self.save_day(day)

    def remove_task(self, id: str):
        task = self.__tasks.get(id)

        if not task:
            raise Exception(f"Task with id {id} not found")

        for date in task.get_dates():
            self.remove_task_from_date(id, date)

        self.__tasks.pop(id)
        # TODO delete task file ? else it gets loaded when program starts

    def remove_task_from_date(self, task_id: str, date: Date):
        day = self.__days[date]
        day.remove_task(task_id)
        self.save_day(day) # TODO delete day and file if no more tasks

    def update_task(self, id: str, description: str | None, start_date: Date | None, end_date: Date | None) -> None:
        task = self.__tasks.get(id)

        if not task:
            raise Exception(f"Task with id {id} not found")

        if description is not None:
            task.description = description

        if start_date is not None:
            if start_date < task.start_date: # add task to new days
                previous_start_date = utilities.get_previous_day(task.start_date)

                for date in utilities.get_dates_between_years(start_date.day, start_date.month, start_date.year, previous_start_date.day, previous_start_date.month, previous_start_date.year):
                    self.add_task_to_date(id, date)

            elif start_date > task.start_date: # remove task from some days
                previous_start_date = utilities.get_previous_day(start_date)

                for date in utilities.get_dates_between_years(task.start_date.day, task.start_date.month, task.start_date.year, previous_start_date.day, previous_start_date.month, previous_start_date.year):
                    self.remove_task_from_date(id, date)

            task.start_date = start_date

        if end_date is not None:
            if end_date > task.end_date: # add task to new days
                next_end_date = utilities.get_next_day(task.end_date)

                for date in utilities.get_dates_between_years(next_end_date.day, next_end_date.month, next_end_date.year, end_date.day, end_date.month, end_date.year):
                    self.add_task_to_date(id, date)

            elif end_date < task.end_date: # remove task from some days
                next_end_date = utilities.get_next_day(end_date)

                for date in utilities.get_dates_between_years(next_end_date.day, next_end_date.month, next_end_date.year, task.end_date.day, task.end_date.month, task.end_date.year):
                    self.remove_task_from_date(id, date)

            task.end_date = end_date

        self.save_task(task)
