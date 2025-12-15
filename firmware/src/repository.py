import json
import os

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

        self.load_data()
        # self.mockup_data()
        print(self.__tasks)
        print(self.__days)
        print("\n")

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

    # --- TESTS

    def get_current_month(self) -> str:
        return "December"

    def get_current_month_first_weekday(self) -> int:
        return 3

    def get_today(self) -> str:
        # return str(self.__today)
        return self.__today

    def get_weekday(self) -> str:
        return "Monday"

    def get_temperature(self):
        return 12