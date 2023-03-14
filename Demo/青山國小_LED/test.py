from machine import LED
import utime as time

led_data = [[0, 0, 0]]*100
first_list = [13, 19,48, 54, 57, 60, 66, 69, 72, 75, 81, 84, 87, 90, 29, 32]


def light_first():
    # led_data = [[0, 0, 0]]*100
    for start in first_list:
        led_data[start] = [255, 0, 255]
        led_data[start] = [255, 0, 255]
        led_data[start] = [255, 0, 255]


    led.rgb_write(led_data)


def light_all():
    led_data = [[255, 0, 255]]*100
    led.rgb_write(led_data)


def off_all():
    led_data = [[0, 0, 0]]*100
    led.rgb_write(led_data)


led = LED(LED.RGB)
led.lightness(100)


while True:
    for i in range(5):
        off_all()
        time.sleep(0.5)
        light_first()
        time.sleep(0.5)

    for i in range(20):
        off_all()
        time.sleep(0.5)
        light_all()
        time.sleep(0.5)
