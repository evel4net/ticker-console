import utime
from machine import Pin
from utime import sleep

from src.date_manager import DateManager
from src.repository import Repository
from src.constants import LED, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN, Color
from src.display import LCD_Display
import src.utilities as utilities
from src.weather_manager import WeatherManager

LED_PIN = Pin(LED, Pin.OUT)
LED_PIN.value(0)

BUTTON_RIGHT_PIN = Pin(BUTTON_RIGHT, Pin.IN, Pin.PULL_DOWN)
BUTTON_LEFT_PIN = Pin(BUTTON_LEFT, Pin.IN, Pin.PULL_DOWN)
BUTTON_MARK_PIN = Pin(BUTTON_UP, Pin.IN, Pin.PULL_DOWN)
BUTTON_DOWN_PIN = Pin(BUTTON_DOWN, Pin.IN, Pin.PULL_DOWN)

class Controller(object):
    def __init__(self, repository: Repository, display: LCD_Display, weather_manager: WeatherManager, date_manager: DateManager) -> None:
        self.__repository = repository
        self.__display = display
        self.__weather_manager = weather_manager
        self.__date_manager = date_manager

        self.__screen_index = 0
        self.__row_index = -1
        self.__change_screen = False
        self.__go_next_row = False
        self.__mark_task = False

        self.__current_day = self.__date_manager.get_today()

        self.setup()

    """BUTTONS + HANDLERS"""

    def setup(self) -> None:
        BUTTON_DOWN_PIN.irq(trigger=Pin.IRQ_RISING, handler=self.__button_down_handler)
        BUTTON_MARK_PIN.irq(trigger=Pin.IRQ_RISING, handler=self.__button_mark_handler)

        BUTTON_LEFT_PIN.irq(trigger=Pin.IRQ_RISING, handler=self.__button_handler)
        BUTTON_RIGHT_PIN.irq(trigger=Pin.IRQ_RISING, handler=self.__button_handler)

    def __button_handler(self, pin: Pin) -> None:
        if not self.__change_screen:
            if pin == BUTTON_LEFT_PIN:
                self.__screen_index -= 1

                if self.__screen_index > 0:
                    self.__current_day = utilities.get_previous_day(self.__current_day)
            elif pin == BUTTON_RIGHT_PIN:
                self.__screen_index += 1

                if self.__screen_index > 1:
                    self.__current_day = utilities.get_next_day(self.__current_day)

            self.__change_screen = True

            if self.__screen_index < -1:
                self.__screen_index = -1
                self.__change_screen = False

    def __button_down_handler(self, pin: Pin) -> None:
        if self.__screen_index > 0 and not self.__go_next_row and pin == BUTTON_DOWN_PIN:
            self.__go_next_row = True

    def __button_mark_handler(self, pin: Pin) -> None:
        if self.__screen_index > 0 and not self.__mark_task and pin == BUTTON_MARK_PIN:
            self.__mark_task = True

    """MANAGE DISPLAY"""

    def start_display(self) -> None:
        self.__draw()

        while True:
            try:
                if self.__change_screen:
                    self.__draw()
            except Exception as e:
                self.__repository.save_error(repr(e))

            sleep(0.05)

    def __draw(self) -> None:
        self.__change_screen = False

        start_pos_x, start_pos_y = -1, -1

        if self.__screen_index < 0:
            self.__display.calendar_screen()
        elif self.__screen_index == 0:
            self.__display.main_screen(self.__repository.get_unfinished_tasks_by_day(self.__current_day))
        else:
            start_pos_x, start_pos_y = self.__display.day_screen(self.__current_day, self.__repository.get_all_tasks_by_day(self.__current_day))
            self.__row_index = -1

        if self.__screen_index == 0:  # refresh clock
            while not self.__change_screen:
                self.__display.draw_clock()

                sleep(0.1)

                # if self.__current_day != self.__date_manager.get_today(): # refresh with new date
                #     print("redraw main screen with new date")
                #     self.__current_day = self.__date_manager.get_today()
                #     self.__change_screen = True

                if self.__date_manager.refresh_today(): # refresh main screen with new date
                    self.__current_day = self.__date_manager.get_today()
                    self.__change_screen = True

                if self.__weather_manager.refresh_weather(): # refresh weather after 30 mins
                    print("redraw weather")
                    self.__display.draw_weather()

        if self.__screen_index > 0:
            while not self.__change_screen:
                if self.__go_next_row:
                    self.__set_cursor(start_pos_x, start_pos_y)
                    self.__go_next_row = False

                if self.__mark_task:
                    self.__mark_task_finished(start_pos_x, start_pos_y)
                    self.__mark_task = False
                    self.__go_next_row = True

                sleep(0.05)

    def __set_cursor(self, start_pos_x: int, start_pos_y: int) -> None:
        self.__row_index += 1

        if self.__row_index >= self.__repository.get_count_tasks(self.__current_day):
            self.__display.draw_text_cursor(start_pos_x, start_pos_y, self.__row_index - 1, Color.BLACK)
            self.__row_index = 0
        elif self.__row_index > 0:
            self.__display.draw_text_cursor(start_pos_x, start_pos_y, self.__row_index - 1, Color.BLACK)

        self.__display.draw_text_cursor(start_pos_x, start_pos_y, self.__row_index, Color.WHITE)

        sleep(0.1)

    def __mark_task_finished(self, start_pos_x: int, start_pos_y: int) -> None:
        if not self.__repository.is_task_finished(self.__current_day, self.__row_index):
            self.__display.draw_task_line(start_pos_x, start_pos_y, self.__row_index, len(self.__repository.get_task_by_index(self.__current_day, self.__row_index).description))
            self.__repository.set_task_finished(self.__current_day, self.__row_index)

        sleep(0.1)

    """LED STATES"""

    def __turn_on_led(self) -> None:
        LED_PIN.value(1)

    def __turn_off_led(self) -> None:
        LED_PIN.value(0)

    def __toggle_led(self) -> None:
        LED_PIN.toggle()