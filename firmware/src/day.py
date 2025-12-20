import src.utilities as utilities
from src.utilities import Date

class Day(object):
    def __init__(self, date: Date, task_ids: list[str] = None, status: list[bool] = None) -> None:  # TODO validate date here or outside?
        self.__date = date

        if task_ids is None:
            task_ids = []
        if status is None:
            status = []

        self.__task_ids = task_ids
        self.__is_finished_status = status

    @property
    def date(self) -> Date:
        return self.__date

    @property
    def tasks(self) -> list[tuple[str, bool]]:
        return list(zip(self.__task_ids, self.__is_finished_status))

    @property
    def unfinished_task_ids(self) -> list[str]:
        indexes = [i for i in range(len(self.__is_finished_status)) if self.__is_finished_status[i] == False]

        return [task_id for i, task_id in enumerate(self.__task_ids) if i in indexes]

    def get_task_id_by_index(self, index: int) -> str:
        return self.__task_ids[index]

    def get_count_tasks(self) -> int:
        return len(self.__task_ids)

    def add_task(self, task_id: str) -> None:
        # self.__tasks[task_id] = False
        self.__task_ids.append(task_id)
        self.__is_finished_status.append(False)

    def remove_task(self, index: int) -> None:
        # self.__tasks.pop(task_id)
        self.__task_ids.pop(index)
        self.__is_finished_status.pop(index)

    def is_task_finished(self, index: int) -> bool:
        return self.__is_finished_status[index]

    def set_task_finished(self, index: int) -> None:
        self.__is_finished_status[index] = True

    def __str__(self) -> str:
        return f"{utilities.date_tuple_to_str(self.__date)}: {self.__task_ids}, {self.__is_finished_status}"

    def __repr__(self) -> str:
        return f"Day(date={utilities.date_tuple_to_str(self.__date)}, task_ids={self.__task_ids}, is_finished_status={self.__is_finished_status})"

    def to_json(self) -> dict:
        return {"date": utilities.date_tuple_to_str(self.__date), "task_ids": self.__task_ids, "is_finished_status": self.__is_finished_status}