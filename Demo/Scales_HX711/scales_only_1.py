from utime import sleep_us, sleep_ms, localtime, time, ticks_ms
from machine import Pin, I2C, LED, Timer, UART
from ePy4Digit import FourDigit
from scales import Scales

i2c0 = I2C(0, I2C.MASTER, baudrate=400000)
disp4 = FourDigit(I2C(1, I2C.MASTER, baudrate=100000))

scales = Scales(d_out=Pin.epy.P14, pd_sck=Pin.epy.P15)  # I2C2
sleep_ms(1000)  # delay 1s for sensor ready
scales.tare()

print("Tare_Done")

ledy = LED('ledy')
ledy.on()

while True:
    weight = scales.stable_value()//1000
    print(weight)  # output
    if weight <= 0:
        weight = 0
    disp4.show4number(weight)
    sleep_ms(100)
