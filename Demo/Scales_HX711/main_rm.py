from machine import RTC
from utime import sleep_us, sleep_ms, localtime, time, ticks_ms
from machine import Pin, I2C, LED, Timer, UART
from ePy4Digit import FourDigit
from htu21d import HTU21D
from scales import Scales
import uos as os
import ujson
import gc


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


def save_config():
    global set_info
    with open('set_info.ini', 'w') as f:
        ujson.dump(set_info, f)


def ble_init_device():
    ble1.write('!CCMD@')
    sleep_ms(200)
    ble1.readline()
    ble1.write('AT+MODE_DATA\r\n')
    sleep_ms(1000)
    ble1.readline()
    ble1.read(ble1.any())  # clear buffer


set_cmd_list = ['setDT', 'setBody', 'setAge',
                'setAmount', 'setToZero', 'setStart', 'setWater_g', 'setMeasInterval']
get_cmd_list = ['getConnState', 'getCupWeight',
                'getDT', 'getTemper', 'getAccwater']


def process_ble_data(ble_data):
    global satrt_measure_flag
    if ble_data == '':
        return
    data = ble_data.split(',')
    if len(data) < 2:
        return
    command = data[0]
    # set command

    if command in set_cmd_list:
        if command == 'setDT' and len(data) == 8:
            now = [int(x) for x in data[1:]]
            now.append(0)
            rtc.datetime(tuple(now))
            set_info['datetime'] = rtc.datetime()
            send_data = 'setDT,1'
        elif command == 'setBody' and data[1].isdigit():
            set_info['body_weight'] = int(data[1])
            send_data = 'setBody,1'
        elif command == 'setAge' and data[1].isdigit():
            set_info['age'] = int(data[1])
            send_data = 'setAge,1'
        elif command == 'setAmount' and data[1].isdigit():
            set_info['water_amount'] = int(data[1])
            send_data = 'setAmount,1'
        elif command == 'setToZero':
            scales.tare()
            send_data = 'setToZero,1'
        elif command == 'setStart':
            satrt_measure_flag = True
            send_data = 'setStart,1'
        elif command == 'setWater_g':
            set_info['water_g'] = int(data[1])
            send_data = 'setWater_g,1'
        elif command == 'setMeasInterval':
            set_info['MeasInterval_s'] = int(data[1])
            send_data = 'setMeasInterval,1'

        ble_SendData(send_data)
        save_config()

    # get Command
    if command in get_cmd_list:
        if command == 'getConnState':
            send_data = 'Connected,1'
        elif command == 'getCupWeight':
            send_data = 'CupWeight,' + str(now_weight)
        elif command == 'getDT':
            dt = rtc.datetime()
            send_data = 'DT,' + str(dt)
        elif command == 'getTemper':
            send_data = 'Temper,' + str(temperature)
        elif command == 'getAccwater':
            send_data = 'Accwater,' + str(acc_water_weight)
        ble_SendData(send_data)


def ble_RecvData():
    if ble1.any():
        msg = ble1.readline()
        _ = ble1.read(ble1.any())
        return (str(msg, 'utf-8'))


def ble_SendData(data):
    _ = ble1.write(data)
    sleep_ms(1)


def Ble_task():
    ble_data = ble_RecvData()
    if ble_data:
        try:
            process_ble_data(ble_data)
        except:
            return


def run_check_water():
    global satrt_measure_flag, acc_water_weight, now_weight, weight
    if satrt_measure_flag:
        # acc_water_weight = 0
        if now_weight < weight:
            record_data = "{}:{}:{} -- drink water weight:{} g".format(
                Clock.hr, Clock.min, Clock.sec, weight-now_weight)
            # print(record_data)
            with open(record_file_name, 'a') as f:
                _ = f.write(record_data+'\r\n')
            acc_water_weight += weight-now_weight
        else:
            record_data = "{}:{}:{} -- add water weight:{} g".format(
                Clock.hr, Clock.min, Clock.sec, now_weight-weight)
            with open(record_file_name, 'a') as f:
                _ = f.write(record_data+'\r\n')
            # print(record_data)


set_info = {'datetime': (2023, 1, 24, 2, 12, 0, 0, 0),
            'water_amount': 100, 'time_threshold': 60, 'body_weight': 20, 'age': 20, 'Water_g': 5000, 'MeasInterval_s': 3600}


def create_info_file():
    global set_info
    try:
        with open('set_info.ini', 'r') as f:
            set_info = ujson.load(f)
    except:
        save_config()


create_info_file()

rtc = RTC()
rtc.datetime(set_info['datetime'])  # set a time for start RTC
ble1 = UART(1, 115200, timeout=20, read_buf_len=512)
i2c0 = I2C(0, I2C.MASTER, baudrate=400000)
sensor = HTU21D(i2c0)
disp4 = FourDigit(I2C(1, I2C.MASTER, baudrate=100000))
Clock = DigitalClock()
scales = Scales(d_out=Pin.epy.P14, pd_sck=Pin.epy.P15)  # I2C2
sleep_ms(500)  # delay 1s for sensor ready
scales.tare()

record_file_name = "water.txt"

ledy = LED('ledy')
ledy.on()

update_water__weight_time = time()
acc_water_weight = 0
water_amount = set_info['water_amount']  # 100 cc
time_threshold = set_info['time_threshold']*60  # 60 second
body_weight = set_info['body_weight']  # Kg
weight = scales.stable_value()//1000
Clock.show_clock(disp4.show_time)
satrt_measure_flag = False
ble_init_device()

while True:
    Ble_task()
    gc.collect()
    now_time = time()
    temperature = sensor.readTemperatureData()
    water_amount = water_amount
    now_weight = scales.stable_value()//1000

    # check start flag
    # if start , record now time ,累積水量歸零
    # 計算累積水量
    # 設定警報是否發報 flag , app 可以下 cmd 取消 flag
    # 判斷累積水量是否到達間隔水量，如果沒有，每秒發出警報聲 (重量改變取消警報)

    if now_weight > 0:
        if weight != now_weight:
            disp4.show4number(now_weight)
            # print(now_weight, now_time)

            weight = now_weight
            update_water_weight_time = now_time

            if (now_time - update_water_weight_time) > time_threshold:
                #print('Over Time--')
                playFreq(1000, 200)
                if acc_water_weight < water_amount:
                    playFreq(3000, 200)
                    #print('Please Drink water--')

    if (now_time % 20) == 0:
        Clock.show_clock(disp4.show_time)
    elif (now_time % 10) == 0:
        disp4.show_temper(temperature)

    sleep_ms(1)
