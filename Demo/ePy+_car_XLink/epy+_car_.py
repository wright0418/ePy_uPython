import utime
from machine import LED, I2C, time_pulse_us, Pin
from machine import display as disp
from machine import Image
import _thread
import uos as os
import ustruct as struct

config_file = 'car_config.txt'


def dj_ctr(cmd):
    # a0, a1, b0, b1, c0, c1
    global config
    angle = 0
    time = 0
    index = 4
    if cmd == 'dj_a0':
        index = 4
        angle = config[0]
        time = config[2]
    elif cmd == 'dj_a1':
        index = 4
        angle = config[1]
        time = config[2]
    elif cmd == 'dj_b0':
        index = 6
        angle = config[3]
        time = config[5]
    elif cmd == 'dj_b1':
        index = 6
        angle = config[4]
        time = config[5]
    # elif cmd == 'dj_c0':
    #     index = 4
    #     angle = config[6]
    #     time = config[8]
    # elif cmd == 'dj_c1':
    #     index = 4
    #     angle = config[7]
    #     time = config[8]
    if time < 10:
        time = 10
    if angle < 0:
        angle = 0
    buf1 = [8, time >> 8, time & 0xff]
    # motor_ctrl.write(1,82,buf1,len(buf1),1)
    motor_ctrl.send(bytearray(buf1), 0x52)

    buf = [index, angle >> 8, angle & 0xff]
    motor_ctrl.send(bytearray(buf), 0x52)


def carforward(speed):
    global motor_ctrl
    motor_ctrl.send(bytearray([0x00, 0x00, speed]), 0x52)
    motor_ctrl.send(bytearray([0x02, 0x00, speed]), 0x52)


def carback(speed):
    global motor_ctrl
    motor_ctrl.send(bytearray([0x00, 0x01, speed]), 0x52)
    motor_ctrl.send(bytearray([0x02, 0x01, speed]), 0x52)


def carleft(speed):
    global motor_ctrl
    motor_ctrl.send(bytearray([0x00, 0x01, speed]), 0x52)
    motor_ctrl.send(bytearray([0x02, 0x00, speed]), 0x52)


def carright(speed):
    global motor_ctrl
    motor_ctrl.send(bytearray([0x00, 0x00, speed]), 0x52)
    motor_ctrl.send(bytearray([0x02, 0x01, speed]), 0x52)


def carstop():
    global motor_ctrl
    motor_ctrl.send(bytearray([0x00, 0x00, 0x00]), 0x52)
    motor_ctrl.send(bytearray([0x02, 0x00, 0x00]), 0x52)


def track():
    global pl, pr
    lv = pl.value()
    rv = pr.value()
    tim = 0
    if lv == 0 and rv == 0:
        carback(10)
        tim = 75
    elif lv == 0 and rv == 1:
        carright(10)
        tim = 80
    elif lv == 1 and rv == 0:
        carleft(10)
        tim = 80
    elif lv == 1 and rv == 1:
        carforward(20)
        tim = 150
    utime.sleep_us(tim)


def UltrasonicRead(trigPin=Pin(Pin.epy.P1, Pin.OUT), echoPin=Pin(Pin.epy.P2, Pin.IN)):
    temperature = 25
    velocity = 331.5 + 0.6*temperature
    trigPin.value(1)
    utime.sleep_us(10)
    trigPin.value(0)
    ret = time_pulse_us(echoPin, 1)
    if ret == -2:
        duration = 0
    elif ret == -1:
        return None
    else:
        duration = ret
    duration = duration/1000000/2
    distance = int(duration*velocity*100)
    utime.sleep_ms(10)
    return distance


def Ultrasonic():
    global ul
    s = UltrasonicRead()
    if s == None:
        return
    # s = s / 10
    if s > 15:
        carforward(20)
    elif s > 10 and s <= 15:
        carforward(20)
    else:
        carstop()
        utime.sleep_ms(50)
        carback(50)
        utime.sleep_ms(400)
        carstop()
        utime.sleep_ms(50)
        carleft(40)
        utime.sleep_ms(400)
        carstop()
        utime.sleep_ms(50)


def controlCar():
    global isRun, ctrModel
    while isRun:
        if ctrModel == 1:
            utime.sleep_ms(100)
        elif ctrModel == 2:
            track()
            utime.sleep_ms(1)
        elif ctrModel == 3:
            Ultrasonic()
            utime.sleep_ms(1)


def rgbLoop():
    global rgb
    for i in range(1, 6):
        rgb.rgb_write(i, 255, 0, 0)
        utime.sleep_ms(100)
    for i in range(1, 6):
        rgb.rgb_write(i, 0, 0, 0)
        utime.sleep_ms(100)


def rgbCtr():
    global isRun, rgbModel, rgb_i, rgb_j, rgb_m, rgb_n, rgb_x, rgb_y
    while isRun:
        if rgbModel == 1:
            rgbLoop()
        elif rgbModel == 2:
            if rgb_i < 255:
                if rgb_j > 5:
                    rgb_i += 1
                    rgb_j = 1
                rgb.rgb_write(rgb_j, rgb_i, 0, 0)
                rgb_j += 1
            elif rgb_m < 255:
                if rgb_n > 5:
                    rgb_m += 1
                    rgb_n = 1
                rgb.rgb_write(rgb_n, 255, rgb_m, 0)
                rgb_n += 1
            elif rgb_x < 255:
                if rgb_y > 5:
                    rgb_x += 1
                    rgb_y = 1
                rgb.rgb_write(rgb_y, 255, 255, rgb_x)
                rgb_y += 1
            else:
                rgb_i = 0
                rgb_j = 1
                rgb_m = 0
                rgb_n = 1
                rgb_x = 0
                rgb_y = 1
            utime.sleep_ms(1)
        else:
            rgb.off()
            utime.sleep(1)


def uint16ToSinged(uint16):
    re = 0
    for i in range(16):
        if uint16 & (0x8000 >> i) != 0:
            if i == 0:
                re = re - pow(2, 15 - i)
            else:
                re = re + pow(2, 15 - i)
    return re


def uploadData():
    asa = bytearray(1)
    buf3 = bytearray(1)
    buf10 = bytearray(1)
    global isRun, ctrModel, ul, motor_ctrl
    while isRun:
        # motor_ctrl.write(1, 12, [49, 2], 2, 1)
        # motor_ctrl.write(1, 12, [1], 1, 1)
        # motor_ctrl.read(1, 12, buf3, 1, 1)
        '''
        motor_ctrl.send(bytearray([49, 2]), 12)
        motor_ctrl.send(bytearray([1]), 12)
        _ = motor_ctrl.recv(buf3, 12)

        data_addr = 17
        data_buf = bytearray(2)
        re = []
        for index in range(3):
            motor_ctrl.send(bytearray([data_addr+index*2]), 12)
            _ = motor_ctrl.recv(data_buf, 12)
            XX = struct.unpack(">h", data_buf)[0]
            utime.sleep_ms(200)
            motor_ctrl.send(bytearray([0x60+index]), 12)
            _ = motor_ctrl.recv(asa, 12)
            X_adj = XX * (asa[0] / 128 + 1)
            re.append(X_adj)
            utime.sleep_ms(200)
        utime.sleep(1)
        print('<<<Compass  x:{0:.3f}  y:{1:.3f} z:{2:.3f}'.format(
            re[0], re[1], re[2]))
        utime.sleep(1)
    '''
        # buffers = [[[17], [18]],
        #            [[19], [20]],
        #            [[21], [22]],
        #            ]

        # re = []

        # for i in range(3):
        #     tmpb = buffers[i]
        #     motor_ctrl.write(1, 12, tmpb[0], 1, 1)
        #     motor_ctrl.read(1, 12, buf3, 1, 1)
        #     motor_ctrl.write(1, 12, tmpb[1], 1, 1)
        #     motor_ctrl.read(1, 12, buf10, 1, 1)

        #     X = (buf10[0] * 256 + buf3[0])
        #     XX = uint16ToSinged(X)

        #     utime.sleep_ms(200)
        #     motor_ctrl.write(1, 12, [0x60 + i], 1, 1)
        #     motor_ctrl.read(1, 12, asa, 1, 1)

        #     X_adj = XX * (asa[0] / 128 + 1)
        #     re.append(X_adj)
        #     utime.sleep_ms(200)

        # utime.sleep(1)
        # print('<<<Compass  x:{0:.3f}  y:{1:.3f} z:{2:.3f}'.format(
        #     re[0], re[1], re[2]))
        # utime.sleep(1)
        if ctrModel != 3:
            s = UltrasonicRead()
            print('Ultrasonic : {} mm'.format(s*10))
        utime.sleep(1)


def sheStateUpload():
    global p3, p4, p12, isRun, p3v, p4v, p12v

    isf = True
    count = 0

    while isRun:
        utime.sleep(2)
        p3new = p3.value()
        p4new = p4.value()
        p12new = p12.value()
        if isf:
            if count < 2:
                count += 1
            else:
                isf = False
            # print('<<<state,{0},{1},{2}'.format(p4new, 1 - p3new, p12new))
            print('state,{0},{1},{2}'.format(p4new, 1 - p3new, p12new))

        if p3new != p3v or p4new != p4v or p12new != p12v:
            p3v = p3new
            p4v = p4new
            p12v = p12new
            # print('<<<state,{0},{1},{2}'.format(p4v, 1 - p3v, p12v))
            print('state,{0},{1},{2}'.format(p4v, 1 - p3v, p12v))


def load_dj_Config():
    # global angle_a_max, angle_a_min, angle_b_max, angle_b_min, angle_c_max, angle_c_min, a_time, b_time, c_time
    # 0, 180, 100, 0, 180, 50, 0, 20, 10
    global config
    _config = []
    if config_file in os.listdir():
        with open(config_file, 'r+') as f:
            mtxt = f.read()
            if len(mtxt) > 0:
                arr = mtxt.split(',')
                if len(arr) >= 9:
                    for l in arr:
                        if l.isdigit():
                            _config.append(int(l))
    if len(_config) >= 9:
        config = []
        for l in _config:
            config.append(l)


def saveConfig():
    global config
    cStr = ''
    for c in config:
        cStr += (str(c) + ',')
    with open(config_file, 'w+') as f:
        f.write(cStr)


def handleConfig(cf):
    global config
    arr = cf.split(',')
    start = 0
    if len(arr) == 4:
        if arr[0] == 'config_a':
            start = 0
        elif arr[0] == 'config_b':
            start = 3
        elif arr[0] == 'config_c':
            start = 6
    config[start] = int(arr[1])
    config[start+1] = int(arr[2])
    config[start+2] = int(arr[3])
    saveConfig()


config = [0, 180, 100, 0, 180, 100,  0, 180, 100]

ctrModel = 1
rgbModel = 0
d = 's'


y = LED('ledy')
g = LED('ledg')
r = LED('ledr')
y.on()

rgb = LED(LED.RGB)
motor_ctrl = I2C(1, I2C.MASTER)
rgb_i = 0
rgb_j = 1
rgb_m = 0
rgb_n = 1
rgb_x = 0
rgb_y = 1

pl = Pin(Pin.epy.P15, Pin.IN)
pr = Pin(Pin.epy.P16, Pin.IN)

# p3 = PIN('P3', mode=PIN.IN)
# p4 = PIN('P4', mode=PIN.IN)
# p12 = PIN('P12', mode=PIN.IN)
p3 = Pin(Pin.epy.P3, Pin.IN)
p4 = Pin(Pin.epy.P4, Pin.IN)
p12 = Pin(Pin.epy.P12, Pin.IN)

p3v = 0
p4v = 0
p12v = 0

p6 = Pin(Pin.epy.P10, Pin.OUT)
p7 = Pin(Pin.epy.P12, Pin.OUT)


try:
    isRun = True
    load_dj_Config()

    _thread.start_new_thread(controlCar, ())
    _thread.start_new_thread(rgbCtr, ())
    # _thread.start_new_thread(uploadData, ())
    # _thread.start_new_thread(sheStateUpload, ())

    print('start ok')

    y.off()
    g.off()
    while isRun:
        d = input()
        if d == 'auto':
            carstop()
            ctrModel = 1
        elif d == 'track':
            carstop()
            ctrModel = 2
        elif d == 'avoid':
            carstop()
            ctrModel = 3
        elif d == 'rgbloop':
            rgbModel = 1
            disp.on()
            disp.show(Image.ARROW_W)
        elif d == 'rgbbre':

            rgb_i = 0
            rgb_j = 1
            rgb_m = 0
            rgb_n = 1
            rgb_x = 0
            rgb_y = 1
            rgbModel = 2
            disp.on()
            disp.show(Image.ARROW_E)
        elif d == 'rgbClose':
            rgb.off()
            rgbModel = 0
            disp.on()
        elif d == 'exit':
            isRun = False
        elif d == 'wpon_z':
            pass
            # if p6.value() == 1 or p7.value() == 1:
            #     p6.value(0)
            #     p7.value(0)
            #     utime.sleep_ms(800)
            # p6.value(1)
            # p7.value(0)
        elif d == 'wpon_f':
            pass
            # if p6.value() == 1 or p7.value() == 1:
            #     p6.value(0)
            #     p7.value(0)
            #     utime.sleep_ms(800)
            # p6.value(0)
            # p7.value(1)
        elif d == 'wpoff':
            pass
            # p6.value(0)
            # p7.value(0)
        elif d.startswith('config'):
            handleConfig(d)
        elif d == 'getconfig':
            cs = ''
            for l in config:
                cs = cs + ',' + str(l)
            print('config' + cs + '\n')
        elif d.startswith('dj_'):
            dj_ctr(d)
        else:
            if ctrModel == 1:
                if d == 's':
                    carstop()
                elif d == 'f':
                    carforward(20)
                elif d == 'b':
                    carback(20)
                elif d == 'l':
                    carleft(20)
                elif d == 'r':
                    carright(20)
        utime.sleep(0.1)
except:
    y.on()
    g.on()
    r.on()
