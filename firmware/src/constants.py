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
DATE_DELIMITER = '_'