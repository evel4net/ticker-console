import json
import os

from src.task import Task
from src.day import Day
import src.utilities as utilities
from src.utilities import Date

class Repository(object):
    def __init__(self) -> None:
        self.__days_path = "./logs/days"
        self.__tasks_path = "./logs/tasks"
        self.__errors_file_path = './logs/errors.txt'

        self.__days = {} # Date(day, month, year): Day
        self.__tasks = {} # task_id: Task

        self.load_data()
        # self.dummy_data()
        # print(self.__tasks)
        # print(self.__days)
        # print("\n")

        # print(self.get_today())
        # print(self.get_weekday())
        # print(self.get_current_month())
        # print(self.get_current_month_first_weekday())

    def dummy_data(self) -> None:
        self.add_task(Task("citit", Date(20, 12, 2025), Date(20, 12, 2025)))
        self.add_task(Task("cumparaturi Craciun", Date(21, 12, 2025), Date(21, 12, 2025)))
        self.add_task(Task("invatat examen practic", Date(20, 12, 2025), Date(20, 12, 2025)))
        self.add_task(Task("scris proiect facultate", Date(20, 12, 2025), Date(22, 12, 2025)))
        self.add_task(Task("curatenie apartament", Date(21, 12, 2025), Date(21, 12, 2025)))
        self.add_task(Task("vizita la bunici", Date(22, 12, 2025), Date(22, 12, 2025)))
        self.add_task(Task("programare sala sport", Date(22, 12, 2025), Date(23, 12, 2025)))
        self.add_task(Task("gatit cina speciala", Date(23, 12, 2025), Date(23, 12, 2025)))
        self.add_task(Task("pregatire prezentare", Date(23, 12, 2025), Date(24, 12, 2025)))
        self.add_task(Task("plimbare in parc", Date(24, 12, 2025), Date(24, 12, 2025)))
        self.add_task(Task("pregatire proiect mare", Date(20, 12, 2025), Date(24, 12, 2025)))
        self.add_task(Task("organizare eveniment facultate", Date(20, 12, 2025), Date(24, 12, 2025)))
        self.add_task(Task("studii pentru examen final", Date(20, 12, 2025), Date(24, 12, 2025)))

    def load_data(self) -> None:
        for filename in os.listdir(self.__days_path):
            filepath = self.__days_path + "/" + filename

            with open(filepath, 'r') as f:
                day = json.load(f)

                date = day["date"]
                tasks = day["task_ids"]
                status = day["is_finished_status"]

                self.__days[utilities.date_str_to_tuple(date)] = Day(utilities.date_str_to_tuple(date), tasks, status)

        for filename in os.listdir(self.__tasks_path):
            filepath = self.__tasks_path + "/" + filename

            with open(filepath, 'r') as f:
                task = json.load(f)

                id = task["id"]
                description = task["description"]
                start_date = task["start_date"]
                end_date = task["end_date"]

                self.__tasks[id] = Task(description, utilities.date_str_to_tuple(start_date), utilities.date_str_to_tuple(end_date), id)

    def save_day(self, day: Day) -> None:
        filepath = self.__days_path + "/" + utilities.date_tuple_to_str(day.date) + ".json"

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
            if date in self.__days.keys():
                day = self.__days[date]
                day.add_task(task.id)

                self.save_day(day)
            else:
                self.add_day(Day(date, [task.id], [False]))

        self.save_task(task)

    def is_task_finished(self, date: Date, index: int) -> bool:
        return self.__days[date].is_task_finished(index)

    def set_task_finished(self, date: Date, index: int) -> None:
        day = self.__days[date]
        day.set_task_finished(index)

        self.save_day(day)

        # print(self.__days)