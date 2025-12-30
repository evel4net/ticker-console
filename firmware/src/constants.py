from dependencies.xglcd_font import XglcdFont
from dependencies.ili9341 import color565

# PINS
LED = 1
BUTTON_LEFT = 7
BUTTON_RIGHT = 6
BUTTON_UP = 8
BUTTON_DOWN = 9

SCK = 14 # serial clock
MOSI = 11 # master-out-slave-in
DC = 13 # data/command
RESET = 15
CS_DUMMY = 0 # chip select (used display doesn't have CS)

# FILE SYSTEM
LOG_DAY_PATH = "./logs/days"
LOG_TASK_PATH = "./logs/tasks"
LOG_ERROR_PATH = "./logs/errors.txt"

# FONTS
class Font:
    ARCADEPIX = XglcdFont('./fonts/ArcadePix9x11.c', 9, 11)
    BALLY = XglcdFont('./fonts/Bally7x9.c', 7, 9)
    DEJAVU = XglcdFont('./fonts/Dejavu24x43.c', 24, 43)
    UNISPACE = XglcdFont('./fonts/Unispace12x24.c', 12, 24)

# COLORS
class Color:
    WHITE = color565(255, 255, 255)
    BLACK = color565(0, 0, 0)
    GREY = color565(100, 100, 100)
    RED = color565(255, 0, 0)
    GREEN = color565(138, 154, 91)

# DISPLAY
PADDING = 10
LINE_SPACING = 10
CURSOR = '*'

# DATE TIME
WEEKDAYS = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
MONTH_DAYS = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
DATE_DELIMITER = '_'

# WEATHER
WEATHERS = {
    0: {
        0: "night-clear",
        1: "day-clear"
    },
    1: {
        0: "night-cloudy",
        1: "day-cloudy"
    },
    2: {
        0: "night-cloudy",
        1: "day-cloudy"
    },
    3: {
        0: "overcast",
        1: "overcast"
    },
    45: {
        0: "fog",
        1: "fog"
    },
    48: {
        0: "fog",
        1: "fog"
    },
    51: {
        0: "showers",
        1: "showers"
    },
    52: {
        0: "showers",
        1: "showers"
    },
    55: {
        0: "showers",
        1: "showers"
    },
    56: {
        0: "showers",
        1: "showers"
    },
    57: {
        0: "showers",
        1: "showers"
    },
    61: {
        0: "rain",
        1: "rain"
    },
    63: {
        0: "rain",
        1: "rain"
    },
    65: {
        0: "rain",
        1: "rain"
    },
    66: {
        0: "rain",
        1: "rain"
    },
    67: {
        0: "rain",
        1: "rain"
    },
    71: {
        0: "night-snow",
        1: "day-snow"
    },
    73: {
        0: "night-snow",
        1: "day-snow"
    },
    75: {
        0: "night-snow",
        1: "day-snow"
    },
    77: {
        0: "night-snow",
        1: "day-snow"
    },
    80: {
        0: "showers",
        1: "showers"
    },
    81: {
        0: "showers",
        1: "showers"
    },
    82: {
        0: "showers",
        1: "showers"
    },
    85: {
        0: "night-snow",
        1: "day-snow"
    },
    86: {
        0: "night-snow",
        1: "day-snow"
    },
    95: {
        0: "thunderstorm",
        1: "thunderstorm"
    },
    96: {
        0: "thunderstorm",
        1: "thunderstorm"
    },
    99: {
        0: "thunderstorm",
        1: "thunderstorm"
    }
}