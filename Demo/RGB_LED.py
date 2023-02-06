from machine import LED
from utime import sleep_ms, sleep
import math

led = LED(LED.RGB)


num_leds = 12
num_streams = 3


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

# 水流燈


def update_stream(stream_index, position):
    for i in range(num_leds):
        if abs(i - position) <= 2:
            color = int(255 * sigmoid(-2 * (position - i)))
            led.rgb_write(i, color, color, color)
        else:
            led.rgb_write(i, 0, 0, 0)


stream_positions = [0 for i in range(num_streams)]
while True:
    for i in range(num_streams):
        stream_positions[i] = (stream_positions[i] + 1) % num_leds
        update_stream(i, stream_positions[i])
    sleep(0.01)
