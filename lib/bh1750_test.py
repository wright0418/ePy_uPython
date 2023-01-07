from machine import I2C, delay
from bh1750 import BH1750

i2c = I2C(0, I2C.MASTER)
s = BH1750(i2c)

while True:
    delay(1)
    #print(s.luminance(BH1750.ONCE_HIRES_1))
    print(s.luminance(BH1750.CONT_HIRES_1))

