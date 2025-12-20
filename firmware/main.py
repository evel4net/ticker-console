from machine import Pin
import network
import rp2
import sys
import utime
import ntptime

from src.controller import Controller
from src.repository import Repository
from src.display import LCD_Display
from src.constants import LED
from src.config_private import SSID, PASSWORD

LED_PIN = Pin(LED, Pin.OUT)
LED_PIN.value(0)

def connect_wifi():
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

def sync_time():
    print("Syncing time...")
    ntptime.settime()

connect_wifi()
# sync_time()

repository = Repository()
display = LCD_Display(repository)
controller = Controller(repository, display)

controller.start_display()