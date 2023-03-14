from machine import LED
import utime
led = LED(LED.RGB)

while True:
    led_data = [[255, 0, 0]]*80
    led.rgb_write(led_data)
    utime.sleep(0.5)
    led_data = [[0, 255, 0]]*80
    led.rgb_write(led_data)
    utime.sleep(0.5)
    led_data = [[0, 0, 255, 0]]*80
    led.rgb_write(led_data)
    utime.sleep(0.5)
