from machine import LED
from utime import sleep_ms, sleep
import math

led = LED(LED.RGB)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def smooth_flow(position, speed):
    for i in range(13):
        brightness = int(255 * sigmoid(speed * (i - position)))
        led.rgb_write(i, brightness, brightness, brightness)
    sleep(0.05)


position = 0
speed = 1

while True:
    position += speed
    if position > 13:
        position = 0
    smooth_flow(position, speed)
