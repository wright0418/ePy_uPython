from machine import time_pulse_us
from machine import I2C
from machine import Pin
from utime import sleep_ms, sleep_us


class EPYCAR():
    def __init__(self):
        self.motor = I2C(1, I2C.MASTER)
        self.led_right = Pin(Pin.epy.P10, Pin.OUT)
        self.led_left = Pin(Pin.epy.P12, Pin.OUT)
        ir_det_left = Pin(Pin.epy.P15, Pin.IN)
        ir_det_right = Pin(Pin.epy.P16, Pin.IN)
        self.trig = Pin(Pin.epy.P1, Pin.OUT)
        self.echo = Pin(Pin.epy.P2, Pin.IN)
        self.led_right.value(0)
        self.led_left.value(0)

    def motor_ctrl(self, FB_speed=0, LR_speed=0):
        w_l = int(FB_speed+LR_speed)
        w_r = int(FB_speed-LR_speed)
        wl = min(max(w_l, -100), 100)
        wr = min(max(w_r, -100), 100)
        motor_l_cmd = [0x00, 0x0, 0x0]
        motor_r_cmd = [0x02, 0x0, 0x0]
        motor_l_cmd[1] = 0x0 if wl > 0 else 0x01
        motor_r_cmd[1] = 0x0 if wr > 0 else 0x01
        motor_l_cmd[2] = (-1*wl) if wl < 0 else wl
        motor_r_cmd[2] = (-1*wr) if wr < 0 else wr
        try:
            self.motor.send(bytearray(motor_l_cmd), 0x52)
            sleep_us(200)
            self.motor.send(bytearray(motor_r_cmd), 0x52)
            sleep_us(200)
        except:
            self.motor = I2C(1, I2C.MASTER)

    def ultrasonic_read(self):
        temperature = 25
        velocity = 331.5 + 0.6*temperature
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)
        ret = time_pulse_us(self.echo, 1)
        if ret == -2:
            duration = 0
        elif ret == -1:
            return None
        else:
            duration = ret
        duration = duration/1000000/2
        distance = int(duration*velocity*100)
        sleep_ms(10)
        return distance


if __name__ == '__main__':
    car = EPYCAR()
    car.motor_ctrl(100, -100)
