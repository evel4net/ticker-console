from machine import Pin, SPI
from dependencies.ili9341 import Display
import utime

from src.repository import Repository
from src.constants import SCK, MOSI, DC, RESET, CS_DUMMY, WEEKDAYS, PADDING, LINE_SPACING, Font, Color, DATE_DELIMITER, \
    CURSOR
from src.config_private import UTC_OFFSET
from src.task import Task
import src.utilities as utilities
from src.utilities import Date

class LCD_Display(object):
    def __init__(self, repository: Repository) -> None:
        self.__repository = repository

        spi = SPI(1,  # SPI channel 1
                baudrate=10000000,  # clock signal Hz
                polarity=1,  # voltage level of clock when not sending data
                phase=1,  # first(0) or second(1) edge of clock signal for sampling data
                bits=8,  # number bits per value
                firstbit=SPI.MSB,  # most significant bit first
                sck=Pin(SCK),
                mosi=Pin(MOSI))

        self.__display = Display(spi, dc=Pin(DC), rst=Pin(RESET), cs=Pin(CS_DUMMY), width=320, height=240, rotation=270)
        self.__display.clear()

    """UTILS"""

    def __date_to_string(self, local) -> str:
        return f"{WEEKDAYS[local[6]]} {utilities.date_tuple_to_str(Date(str(local[2]), str(local[1]), str(local[0])), "/")}"

    def __time_to_string(self, local) -> str:
        # return f"{str(local[3])}:{str(local[4])}:{str(local[5])}"
        hours = local[3] + UTC_OFFSET
        minutes = local[4]
        return f"{"0" + str(hours) if hours < 10 else str(hours)}:{"0" + str(minutes) if minutes < 10 else str(minutes)}"

    def __local_to_date(self, local) -> Date:
        return Date(local[2], local[1], local[0])

    """DRAW COMPONENTS"""

    def draw_main_frame(self) -> None:
        pos_y = PADDING + Font.DEJAVU.height + Font.UNISPACE.height + 3 * LINE_SPACING
        self.__display.draw_line(0, pos_y, self.__display.width - 1, pos_y, Color.WHITE)

        pos_x = int(self.__display.width / 2) + 40
        self.__display.draw_line(pos_x, 0, pos_x, pos_y, Color.WHITE)

    def draw_clock(self) -> (int, int):
        self.__display.draw_text(PADDING, PADDING, self.__time_to_string(utime.localtime()), Font.DEJAVU, Color.WHITE)

        return PADDING, PADDING + Font.DEJAVU.height + LINE_SPACING

    def draw_date(self, pos_x, pos_y, date: Date) -> (int, int):
        self.__display.draw_text(pos_x, pos_y, utilities.date_tuple_to_str(date, '/'), Font.UNISPACE, Color.WHITE)

        return pos_x, pos_y + Font.UNISPACE.height + LINE_SPACING

    def draw_weather(self) -> None:
        pos_x = int(self.__display.width / 2) + 60
        pos_y = int((PADDING + LINE_SPACING + Font.UNISPACE.height) / 2)

        temperature, precipitation, weather_code = self.__repository.get_weather()

        self.__display.draw_text(pos_x, pos_y, f"{str(temperature)} C", Font.UNISPACE, Color.WHITE)
        self.__display.draw_text(pos_x, pos_y + Font.UNISPACE.height + 10, f"{str(precipitation)}%", Font.ARCADEPIX, Color.WHITE)

    def draw_tasks(self, pos_x, pos_y, tasks: list[tuple[Task, bool]]) -> (int, int):
        for task, is_finished in tasks:
            self.__display.draw_text(pos_x, pos_y, f"  {task.description}", Font.ARCADEPIX, Color.WHITE)

            if is_finished:
                self.__display.draw_line(pos_x + Font.ARCADEPIX.width, pos_y + int(Font.ARCADEPIX.height / 2), pos_x + Font.ARCADEPIX.width * len(task.description), pos_y + int(Font.ARCADEPIX.height / 2),  Color.WHITE)

            pos_y += Font.ARCADEPIX.height + LINE_SPACING

        return pos_x, pos_y

    def draw_task_line(self, start_pos_x: int, start_pos_y: int, day: Date, task_index: int) -> (int, int):
        task = self.__repository.get_task_by_index(day, task_index)

        pos_y = start_pos_y + task_index * (Font.ARCADEPIX.height + LINE_SPACING) + int(Font.ARCADEPIX.height / 2)
        pos_x = start_pos_x + Font.ARCADEPIX.width
        self.__display.draw_line(pos_x, pos_y, pos_x + Font.ARCADEPIX.width * len(task.description), pos_y, Color.WHITE)

        return start_pos_x, pos_y + int(Font.ARCADEPIX.height / 2) + LINE_SPACING

    def draw_text_cursor(self, start_pos_x: int, start_pos_y: int, task_index: int, cursor_color: Color) -> (int, int):
        pos_y = start_pos_y + task_index * (Font.ARCADEPIX.height + LINE_SPACING)

        self.__display.draw_text(start_pos_x, pos_y, CURSOR, Font.ARCADEPIX, color=cursor_color)

        return start_pos_x, pos_y

    def draw_calendar(self) -> None:
        left_top_x = 6
        left_top_y = 40

        right_bottom_x = 307
        right_bottom_y = 229

        cell_height = int((right_bottom_y - left_top_y) / 7)
        cell_width = int((right_bottom_x - left_top_x) / 7)

        # HEADER
        self.__display.fill_hrect(left_top_x, left_top_y, right_bottom_x - left_top_x, cell_height, Color.GREEN)

        # FRAME
        pos_y = left_top_y

        for i in range(8):
            self.__display.draw_line(left_top_x, pos_y, right_bottom_x, pos_y, Color.GREY)
            pos_y += cell_height

        pos_x = left_top_x

        for i in range(8):
            self.__display.draw_line(pos_x, left_top_y, pos_x, right_bottom_y, Color.GREY)
            pos_x += cell_width

        # WEEKDAYS
        pos_y = left_top_y + 1 + int((cell_height - Font.UNISPACE.height - 1) / 2)
        pos_x = left_top_x + 1 + int((cell_width - Font.UNISPACE.width - 1) / 2)

        for day in WEEKDAYS.values():
            self.__display.draw_text(pos_x, pos_y, day[:1], Font.UNISPACE, Color.BLACK, background=Color.GREEN)
            pos_x += cell_width

        # DAYS
        weekday = self.__repository.get_week_day_of_current_month(1)

        pos_x = left_top_x + 1 + int((cell_width - Font.UNISPACE.width * 2 - 1) / 2) + weekday * cell_width
        pos_y += cell_height + 1

        current_day = self.__repository.get_today().day
        max_days = self.__repository.get_total_number_days_in_current_month()

        for i in range(max_days):
            self.__display.draw_text(pos_x, pos_y, str(i + 1), Font.UNISPACE, Color.WHITE)

            if i == current_day - 1:
                self.__display.draw_circle(pos_x + Font.UNISPACE.width, pos_y + int(Font.UNISPACE.height / 2) - 2,
                                           int(cell_height / 2) + 2, Color.RED)

            pos_x += cell_width

            if pos_x > 316:
                pos_x = left_top_x + 1 + int((cell_width - Font.UNISPACE.width * 2 - 1) / 2)
                pos_y += cell_height

    """DRAW SCREENS"""

    def main_screen(self) -> (int, int):
        self.__display.clear()

        self.draw_main_frame()
        current_pos_x, current_pos_y = self.draw_clock()
        current_pos_x, current_pos_y = self.draw_date(current_pos_x, current_pos_y, self.__local_to_date(utime.localtime()))
        self.draw_tasks(current_pos_x, current_pos_y + 3 * LINE_SPACING, self.__repository.get_unfinished_tasks_by_day(self.__repository.get_today()))
        self.draw_weather()

        return current_pos_x, current_pos_y + 3 * LINE_SPACING

    def calendar_screen(self) -> None:
        self.__display.clear()

        self.__display.draw_text(PADDING, PADDING, self.__repository.get_current_month(), Font.UNISPACE, Color.WHITE)
        self.draw_calendar()

    def day_screen(self, day: Date) -> (int, int):
        self.__display.clear()

        current_pos_x, current_pos_y = self.draw_date(PADDING, PADDING, day)

        self.__display.draw_line(0, current_pos_y, self.__display.width - 1, current_pos_y, Color.WHITE)

        self.draw_tasks(current_pos_x, current_pos_y + LINE_SPACING, self.__repository.get_all_tasks_by_day(day))

        return current_pos_x, current_pos_y + LINE_SPACING