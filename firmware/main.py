import asyncio

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
from src.web_server import WebServer

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

def sync_time() -> None:
    print("Syncing time...")
    ntptime.settime()

connect_wifi()
sync_time()

repository = Repository()
web_server = WebServer(repository)

weather_manager = WeatherManager()
date_manager = DateManager()
display = LCD_Display(weather_manager, date_manager)
controller = Controller(repository, display, weather_manager, date_manager)

async def main():
    asyncio.create_task(web_server.start_server())
    asyncio.create_task(controller.start_display())

    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.create_task(main())

print("Starting loop...")

try:
    loop.run_forever()
except Exception as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("Program interrupted from keyboard")
finally:
    web_server.stop_server()
    loop.close()