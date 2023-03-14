from machine import Pin, LED
from ePyButton import Button
from utime import sleep


def handle_press():
    print("Button pressed")
    y_led.on()


def handle_release():
    print("Button released")
    y_led.off()


def handle_hold(time):
    print("Button held for {}ms".format(time))
    r_led.toggle()


def handle_double_press():
    print("Button double pressed")
    g_led.toggle()


# Pin.epy.P24 KeyA
button = Button(Pin.epy.P24)

button.when_double_pressed(handle_double_press)
button.when_pressed(handle_press)
button.when_released(handle_release)
button.when_held(handle_hold, hold_time=2000)

y_led = LED('ledy')
r_led = LED('ledr')
g_led = LED('ledg')

while True:
    pass
