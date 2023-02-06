from machine import RTC
from utime import sleep_us, sleep_ms, localtime, time, ticks_ms
from machine import Pin, I2C, LED, Timer, UART
from ePy4Digit import FourDigit
from htu21d import HTU21D
from scales import Scales
import RL62M
import uos as os
import ujson


timer = Timer(0)
buzzer = Pin(Pin.epy.P9, Pin.OUT)


def toggle_buzzer(t):
    buzzer.value(~buzzer.value() & 0x0001)


def playFreq(playFreq, playtime_ms):
    timer.init(freq=int(playFreq*2))
    timer.callback(toggle_buzzer)
    preTime = ticks_ms()
    while (ticks_ms() - preTime) < (playtime_ms):
        sleep_ms(1)
    timer.callback(None)


class DigitalClock:
    def __init__(self):
        self.hr, self.min, self.sec = localtime()[3:6]

    def show_clock(self, disp):
        self.hr, self.min, self.sec = localtime()[3:6]
        #print("time = {}:{}:{}".format(self.hr, self.min, self.sec))
        # show Hr: Min to Display
        disp(self.hr, self.min)


def Ble_task():
    global walter_amount, set_info, temperature, acc_walter_weight
    BLEData = BLE.RecvData()
    if BLE.state != 'CONNECTED' or BLEData == '':
        return
    data = BLEData.split(',')
    # print(data)
    # set dateTime
    try:
        if data[0] == 'setDT' and len(data) == 8:
            now = [int(x) for x in data[1:]]
            now.append(0)
            rtc.datetime(tuple(now))
            set_info['datetime'] = rtc.datetime()
            with open('set_info.ini', 'w') as f:
                ujson.dump(set_info, f)
        if data[0] == 'setBody' and data[1].isdigit:
            set_info['body_weight'] = int(data[1])
            with open('set_info.ini', 'w') as f:
                ujson.dump(set_info, f)
            #print('setboday', int(data[1]))

        if data[0] == 'setAmount' and data[1].isdigit:
            set_info['walter_amount'] = int(data[1])
            with open('set_info.ini', 'w') as f:
                ujson.dump(set_info, f)
            #print('walter_amount', int(data[1]))

        if data[0] == 'getDT':
            dt = rtc.datetime()
            sendData = 'DT,' + str(dt)
            BLE.SendData(sendData)
            sleep_us(10)
        if data[0] == 'getTemper':
            sendData = 'Temper,' + str(temperature)
            BLE.SendData(sendData)
            sleep_us(10)
        if data[0] == 'getAccWalter':
            sendData = 'AccWalter,' + str(acc_walter_weight)
            BLE.SendData(sendData)
            sleep_us(10)
    except:
        return


set_info = {'datetime': (2023, 1, 24, 2, 12, 0, 0, 0),
            'walter_amount': 100, 'time_threshold': 60, 'body_weight': 20}


def create_info_file():
    global set_info
    try:
        with open('set_info.ini', 'r') as f:
            set_info = ujson.load(f)
    except:
        with open('set_info.ini', 'w') as f:
            ujson.dump(set_info, f)


create_info_file()
rtc = RTC()
rtc.datetime(set_info['datetime'])  # set a time for start RTC

ble1 = UART(1, 115200, timeout=20, read_buf_len=64)
BLE = RL62M.GATT(ble1)
i2c0 = I2C(0, I2C.MASTER, baudrate=400000)
sensor = HTU21D(i2c0)
disp4 = FourDigit(I2C(1, I2C.MASTER, baudrate=100000))
Clock = DigitalClock()
scales = Scales(d_out=Pin.epy.P14, pd_sck=Pin.epy.P15)  # I2C2
sleep_ms(500)  # delay 1s for sensor ready
scales.tare()

record_file_name = "walter.txt"

ledy = LED('ledy')
ledy.on()

update_walter__weight_time = time()
acc_walter_weight = 0
walter_amount = set_info['walter_amount']  # 100 cc
time_threshold = set_info['time_threshold']*60  # 60 second
body_weight = set_info['body_weight']  # Kg

weight = scales.stable_value()//1000
Clock.show_clock(disp4.show_time)
# print('Start')
while True:
    Ble_task()
    now_time = time()

    temperature = sensor.readTemperatureData()

    walter_amount = walter_amount + int(temperature)
    now_weight = scales.stable_value()//1000
    if now_weight > 0:
        if weight != now_weight:
            disp4.show4number(now_weight)
            if now_weight < weight:
                record_data = "{}:{}:{} -- drink walter weight:{} g".format(
                    Clock.hr, Clock.min, Clock.sec, weight-now_weight)
                # print(record_data)
                with open(record_file_name, 'a') as f:
                    _ = f.write(record_data+'\r\n')
                acc_walter_weight += weight-now_weight
            else:
                record_data = "{}:{}:{} -- add walter weight:{} g".format(
                    Clock.hr, Clock.min, Clock.sec, now_weight-weight)
                with open(record_file_name, 'a') as f:
                    _ = f.write(record_data+'\r\n')
                # print(record_data)
            weight = now_weight
            update_walter__weight_time = now_time

            if (now_time - update_walter__weight_time) > time_threshold:
                #print('Over Time--')
                playFreq(1000, 200)
                if acc_walter_weight < walter_amount:
                    playFreq(3000, 200)
                    #print('Please Drink walter--')

    elif (now_time % 20) == 0:
        Clock.show_clock(disp4.show_time)
    elif (now_time % 10) == 0:
        disp4.show_temper(temperature)
    sleep_ms(1)
