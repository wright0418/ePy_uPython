from machine import Pin, Timer
from utime import ticks_ms


class Button:
    def __init__(self, pin, hold_time=1000):
        self.pin = Pin(pin, Pin.IN)
        self.hold_time = hold_time
        self.timer = Timer(0)
        self._active = False
        self._last_state = self.pin.value()
        self._pressed_time = 0
        self._released_time = 0
        self._held_time = 0
        self._callback_pressed = None
        self._callback_released = None
        self._callback_held = None
        self._callback_double_pressed = None
        self._last_pressed_time = 0
        self.timer.init(freq=1000//50, callback=self._timer_callback)

    def _timer_callback(self, timer):
        state = self.pin.value()
        if state != self._last_state:
            self._last_state = state
            if state == 0:
                self._released_time = self._held_time = 0
                self._pressed_time = ticks_ms()
                if self._callback_pressed:
                    self._callback_pressed()
                    if self._last_pressed_time != 0 and self._pressed_time - self._last_pressed_time < 500:
                        self._last_pressed_time = 0
                        if self._callback_double_pressed:
                            self._callback_double_pressed()
                    else:
                        self._last_pressed_time = self._pressed_time
            else:
                self._pressed_time = self._held_time = 0
                self._released_time = ticks_ms()
                if self._callback_released:
                    self._callback_released()

        elif state == 0 and self._active:
            held_time = ticks_ms() - self._pressed_time
            if held_time >= self.hold_time:
                self._held_time = held_time
                if self._callback_held:
                    self._callback_held(self._held_time)
            else:
                self._held_time = 0

        self._active = state == 0

    def when_pressed(self, callback):
        self._callback_pressed = callback

    def when_released(self, callback):
        self._callback_released = callback

    def when_held(self, callback, hold_time=None):
        if hold_time is not None:
            self.hold_time = hold_time
        self._callback_held = callback

    def when_double_pressed(self, callback):
        self._callback_double_pressed = callback

    def value(self):
        return self.pin.value()


if __name__ == '__main__':
    from machine import Pin
    button = Button(Pin.epy.P24)

    def handle_press():
        print("Button pressed")

    def handle_release():
        print("Button released")

    def handle_hold(time):
        print("Button held for {}ms".format(time))

    def handle_double_press():
        print("Button double pressed")

    button.when_double_pressed(handle_double_press)
    button.when_pressed(handle_press)
    button.when_released(handle_release)
    button.when_held(handle_hold, hold_time=2000)

    while True:
        pass
