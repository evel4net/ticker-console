# Ticker Console Firmware

Device uses an LCD screen, physical buttons and custom MicroPython firmware which handles:
- real-time clock and weather display
- monthly calendar display
- daily and upcoming tasks
- HTTP web server for future communication with a possible phone or web app
- secure authentication and communication over the network 

## Planned Work

- [x] connect SPI LCD Display and buttons to Raspberry Pi Pico 2W
- [x] implement display graphics and button controls
- [x] manage the file system for saving data: save as JSON files
- [x] connect to a weather API and display the real-time weather
- [x] implement HTTP web server with requests
- [x] add authentification for HTTP requests
- [x] add encryption/decryption for HTTP message body
- [x] modify server to accept multiple clients concurrently
- [ ] fix server encryption when receiving an invalid/not authorized request 
- [ ] protect shared resources when accepting multiple clients

Optional:
- scroll for tasks when too many
- additional buttons: shut down, change mode

## Setting up Pico

- install MicroPython by flashing the UF2 firmware (https://micropython.org/download/) using BOOTSEL model
- install `requirements-dev.txt` in the IDE (`pip install -r requirements-dev.txt`)

## References

Used libraries and resources:
- https://micropython.org/
- https://github.com/rdagger/micropython-ili9341 (LCD display driver)
- https://pypi.org/project/micropython-rp2-stubs/
- https://open-meteo.com/en/docs (Weather API)
- https://erikflowers.github.io/weather-icons/ (Weather Icons)
- https://github.com/lc6chang/ecc-pycrypto (ECC asymmetric key + ECDH shared secret, modified the code to work with MicroPython)
- https://github.com/micropython/micropython-lib/blob/master/python-stdlib/hmac/hmac.py (HMAC)

Learning resources:
- https://bytesnbits.co.uk/raspberry-pi-pico-spi-lcd-display/
- https://ia801803.us.archive.org/27/items/rpi-pico-micropython/RPi_PiPico_Digital_v10.pdf
- https://projects.raspberrypi.org/en/projects/get-started-pico-w
- https://docs.micropython.org/en/latest/library/index.html
- https://randomnerdtutorials.com/raspberry-pi-pico-w-http-requests-micropython/
- https://randomnerdtutorials.com/raspberry-pi-pico-w-asynchronous-web-server-micropython/
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication
- https://hwwong168.wordpress.com/2019/09/25/esp32-micropython-implementation-of-cryptographic/
- https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.198-1.pdf (HMAC algorithm)

RP2040 Microcontroller Datasheet: https://pip-assets.raspberrypi.com/categories/814-rp2040/documents/RP-008371-DS-1-rp2040-datasheet.pdf?disposition=inline
