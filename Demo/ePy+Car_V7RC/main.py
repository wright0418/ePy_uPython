from V7RC import V7RC
from EPYCAR import EPYCAR
from utime import sleep_ms


v7rc = V7RC()
car = EPYCAR()
while True:
    type, channel_data = v7rc.read()
    if type:
        if type == 'SRV':

            fb_speed = (channel_data[1]-1500)//5
            lr_speed = (channel_data[0]-1500)//5
            car.motor_ctrl(fb_speed, lr_speed)

    sleep_ms(50)
