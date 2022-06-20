import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import secrets
import time
# print("Raspberry Pi Pico WiFi Weather Station")
# JSON_URL = f"http://api.openweathermap.org/data/2.5/weather?q=LOCATIONl&appid={secrets["weatherAPIKey"]}&units=metric"

PIN_SCK = board.GP2
PIN_MOSI = board.GP3
PIN_MISO = board.GP4

PIN_ESPCS = board.GP19
PIN_ESPBUSY = board.GP18
PIN_ESPRST = board.GP17

esp32_cs = DigitalInOut(PIN_ESPCS)
esp32_ready = DigitalInOut(PIN_ESPBUSY)
esp32_reset = DigitalInOut(PIN_ESPRST)

spi = busio.SPI(PIN_SCK, PIN_MOSI, PIN_MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
requests.set_socket(socket, esp)

def getNetTime() :
    JSON_URL="https://worldtimeapi.org/api/timezone/PST8PDT"

    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue

    print("Fetching time")
    r = requests.get(JSON_URL)
    print(r.json())
    return time.localtime(r.json()["unixtime"] )