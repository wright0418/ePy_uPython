from machine import time_pulse_us
from machine import I2C
from machine import Pin
from utime import sleep_ms, sleep_us
from machine import LED
from machine import UART
import ure as re
import gc


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


class V7RC():
    def __init__(self):
        try:
            self.ble = UART(1, 115200, timeout=20, read_buf_len=64)
        except:
            self.ble.deinit()
            self.ble = UART(1, 115200, timeout=20, read_buf_len=64)

    def read(self):
        data = self.ble.readline()
        if data != b'':
            data_formats = [('SRT', r'SRT[0-9]*?#'),
                            ('SRV', r'SRV[0-9]*?#'),
                            ('SS8', r'SS8[A-F,0-9]*?#'),
                            ('SR2', r'SR2[A-F,0-9]*?#'),
                            ('LED', r'LED[A-F,0-9]*?#'),
                            ('LE2', r'LE2[A-F,0-9]*?#')]
            try:
                for name, regex in data_formats:
                    ss = re.search(regex, data)
                    if ss and name in ('SS8', 'SR2', 'LED', 'LE2'):
                        ch_data = [int(ss.group(0)[i:i+2], 16)
                                   for i in range(3, 19, 2)]
                        return (name, ch_data)
                    elif ss and name in ('SRT', 'SRV'):
                        # print(ss.group(0))
                        ch_data = [int(ss.group(0)[i:i+4])
                                   for i in range(3, 19, 4)]
                        # print(name, ch_data)
                        return (name, ch_data)
            except:
                print('except')
                pass
        return (None, None)


y = LED('ledy')
v7rc = V7RC()
car = EPYCAR()
y.on()
try:
    while True:
        type, channel_data = v7rc.read()
        if type:
            if type == 'SRV':
                y.on()
                fb_speed = (channel_data[1]-1500)//5
                lr_speed = (channel_data[0]-1500)//5
                # print(fb_speed, lr_speed)
                car.motor_ctrl(fb_speed, lr_speed)
                sleep_ms(20)
                y.off()
        # sleep_ms(1)
        gc.collect()
except:
    y.off()
