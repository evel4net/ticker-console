from machine import Pin
import network
import rp2
import sys
import utime
import ntptime

from src.controller import Controller
from src.date_manager import DateManager
from src.repository import Repository
from src.display import LCD_Display
from src.constants import LED
from src.config_private import SSID, PASSWORD
from src.weather_manager import WeatherManager

LED_PIN = Pin(LED, Pin.OUT)
LED_PIN.value(0)

def connect_wifi() -> None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1: # quit program when BOOTSEL button is pressed
            print("STOP")
            sys.exit()

        print("Connecting to WiFi...")
        LED_PIN.value(1)
        utime.sleep(0.5)
        LED_PIN.value(0)
        utime.sleep(0.5)


    print(wlan.ifconfig())

def sync_time() -> None:
    print("Syncing time...")
    ntptime.settime()

# connect_wifi()
# sync_time()

repository = Repository()
weather_manager = WeatherManager()
date_manager = DateManager()
display = LCD_Display(weather_manager, date_manager)
controller = Controller(repository, display, weather_manager, date_manager)

controller.start_display()