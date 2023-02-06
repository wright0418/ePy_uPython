import utime as time
import urandom as random
from utime import sleep_ms, sleep
from machine import LED
i

led_count = 64
led = LED(LED.RGB)

while True:
    for i in range(led_count):
        led_index = random.randint(0, led_count - 1)
        led.rgb_write(led_index, 255, 255, 255)
        time.sleep(0.05)
        led.rgb_write(led_index, 0, 0, 0)
