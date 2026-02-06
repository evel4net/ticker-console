from machine import Pin, SPI
from dependencies.ili9341 import Display
import utime

from src.date_manager import DateManager
from src.constants import SCK, MOSI, DC, RESET, CS_DUMMY, WEEKDAYS, PADDING, LINE_SPACING, Font, Color, \
    CURSOR, WEATHERS
from src.task import Task
import src.utilities as utilities
from src.utilities import Date
from src.weather_manager import WeatherManager


class LCD_Display(object):
    def __init__(self, weather_manager: WeatherManager, date_manager: DateManager) -> None:
        self.__weather_manager = weather_manager
        self.__date_manager = date_manager

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

    def __today_to_main_string(self) -> str:
        current_date = self.__date_manager.get_today()

        weekday = self.__date_manager.get_week_day_of_current_month(current_date.day)

        return f"{WEEKDAYS[weekday]} {utilities.date_tuple_to_str(current_date, "/")}"

    def __local_to_time_string(self, local) -> str:
        hours, minutes, _ = utilities.local_to_actual_time(local)

        return f"{"0" + str(hours) if hours < 10 else str(hours)}:{"0" + str(minutes) if minutes < 10 else str(minutes)}"

    """DRAW COMPONENTS"""

    def draw_main_frame(self) -> None:
        # pos_y = PADDING + Font.DEJAVU.height + Font.UNISPACE.height + 3 * LINE_SPACING
        pos_y = PADDING + Font.DEJAVU.height + LINE_SPACING + Font.UNISPACE.height + PADDING
        self.__display.draw_line(0, pos_y, self.__display.width - 1, pos_y, Color.WHITE)

        # pos_x = int(self.__display.width / 2) + 20
        pos_x = 188
        self.__display.draw_line(pos_x, 0, pos_x, pos_y, Color.WHITE)

    def draw_clock(self) -> (int, int):
        self.__display.draw_text(PADDING, PADDING, self.__local_to_time_string(utime.localtime()), Font.DEJAVU, Color.WHITE)

        return PADDING, PADDING + Font.DEJAVU.height + LINE_SPACING

    def draw_date(self, pos_x, pos_y, date_text: str) -> (int, int):
        self.__display.draw_text(pos_x, pos_y, date_text, Font.UNISPACE, Color.WHITE)

        return pos_x, pos_y + Font.UNISPACE.height + LINE_SPACING

    def draw_weather(self) -> None:
        pos_x = 188 + PADDING
        pos_y = PADDING + Font.DEJAVU.height + LINE_SPACING + int((Font.UNISPACE.height - 16) / 2)

        # clean weather part
        self.__display.fill_hrect(pos_x, 0, self.__display.width - pos_x, pos_y + Font.UNISPACE.height, Color.BLACK)

        # display current weather
        temperature, precipitation, weather_code, is_day = self.__weather_manager.get_weather()

        # images
        self.__display.draw_image("icons/raindrop.raw", pos_x, pos_y, 12, 16)

        pos_x = self.__display.width - 64
        pos_y = int((PADDING * 2 + LINE_SPACING + Font.DEJAVU.height + Font.UNISPACE.height - 64) / 2)

        try:
            self.__display.draw_image(f"icons/{WEATHERS[weather_code][is_day]}.raw", pos_x, pos_y, 64, 64)
        except OSError:
            self.__display.draw_image(f"icons/na.raw", pos_x, pos_y, 64, 64)

        # values
        pos_x = 188 + PADDING

        pos_y = PADDING
        self.__display.draw_text(pos_x, pos_y, f"{temperature}*C", Font.UNISPACE, Color.WHITE)

        pos_y = PADDING + Font.DEJAVU.height + LINE_SPACING + int((Font.UNISPACE.height - Font.ARCADEPIX.height) / 2)
        self.__display.draw_text(pos_x + 12 + PADDING - 1, pos_y, f"{precipitation}%", Font.ARCADEPIX, Color.WHITE)

    def draw_tasks(self, pos_x, pos_y, tasks: list[tuple[Task, bool]]) -> (int, int):
        for task, is_finished in tasks:
            self.__display.draw_text(pos_x, pos_y, f"  {task.description}", Font.ARCADEPIX, Color.WHITE)

            if is_finished:
                self.__display.draw_line(pos_x + Font.ARCADEPIX.width, pos_y + int(Font.ARCADEPIX.height / 2), pos_x + Font.ARCADEPIX.width * len(task.description), pos_y + int(Font.ARCADEPIX.height / 2),  Color.WHITE)

            pos_y += Font.ARCADEPIX.height + LINE_SPACING

        return pos_x, pos_y

    def draw_task_line(self, start_pos_x: int, start_pos_y: int, task_index: int, length: int) -> (int, int):
        pos_y = start_pos_y + task_index * (Font.ARCADEPIX.height + LINE_SPACING) + int(Font.ARCADEPIX.height / 2)
        pos_x = start_pos_x + Font.ARCADEPIX.width
        self.__display.draw_line(pos_x, pos_y, pos_x + Font.ARCADEPIX.width * length, pos_y, Color.WHITE)

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
        weekday = self.__date_manager.get_week_day_of_current_month(1)

        pos_x = left_top_x + 1 + int((cell_width - Font.UNISPACE.width * 2 - 1) / 2) + weekday * cell_width
        pos_y += cell_height + 1

        current_day = self.__date_manager.get_today().day
        max_days = self.__date_manager.get_number_days_in_current_month()

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

    def main_screen(self, tasks: list[tuple[Task, bool]]) -> (int, int):
        self.__display.clear()

        self.draw_main_frame()
        current_pos_x, current_pos_y = self.draw_clock()
        current_pos_x, current_pos_y = self.draw_date(current_pos_x, current_pos_y, self.__today_to_main_string())
        self.draw_tasks(current_pos_x, current_pos_y + LINE_SPACING, tasks)
        self.draw_weather()

        return current_pos_x, current_pos_y + 3 * LINE_SPACING

    def calendar_screen(self) -> None:
        self.__display.clear()

        self.__display.draw_text(PADDING, PADDING, self.__date_manager.get_current_month(), Font.UNISPACE, Color.WHITE)
        self.draw_calendar()

    def day_screen(self, day: Date, tasks: list[tuple[Task, bool]]) -> (int, int):
        self.__display.clear()

        current_pos_x, current_pos_y = self.draw_date(PADDING, PADDING, utilities.date_tuple_to_str(day, '/'))

        self.__display.draw_line(0, current_pos_y, self.__display.width - 1, current_pos_y, Color.WHITE)

        self.draw_tasks(current_pos_x, current_pos_y + LINE_SPACING, tasks)

        return current_pos_x, current_pos_y + LINE_SPACING