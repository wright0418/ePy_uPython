from machine import UART
import ure as re
from utime import sleep_ms
try:
    ble = UART(1, 115200, timeout=20, read_buf_len=64)
except:
    ble.deinit()
    ble = UART(1, 115200, timeout=20, read_buf_len=64)


def V7RC_read():
    data = ble.readline()
    if data != b'':
        # SRV1500150015001500# -> C1, C2, C3, C4 PWM訊號
        ss = re.search(r'SRT[0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+4]) for i in range(3, 19, 4)]
            return ('SRT', ch_data)
        # SRT1500150015001500# -> C1, C2, C3, C4 PWM訊號
        ss = re.search(r'SRV[0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+4]) for i in range(3, 19, 4)]
            return ('SRV', ch_data)
        # SR21500100018002000# -> C5, C6, C7, C8 PWM訊號

        ss = re.search(r'SS8[A-F,0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+2], 16) for i in range(3, 18, 2)]
            return ('SS8', ch_data)
        # SS89696969696969669# -> 簡易PWM. 可同時使用8個PWM
        ss = re.search(r'SR2[A-F,0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+2], 16) for i in range(3, 18, 2)]
            return ('SR2', ch_data)
        # LEDFFFAFFFAFFFAFFFA# -> 控制前方的LED
        ss = re.search(r'LED[A-F,0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+2], 16) for i in range(3, 18, 2)]
            return ('LED', ch_data)
        # LE2FFFAFFFAFFFAFFFA# -> 控制前方的LE2
        ss = re.search(r'LE2[A-F,0-9]*?#', data)
        if ss:
            ch_data = [int(ss.group(0)[i:i+2], 16) for i in range(3, 18, 2)]
            return ('LE2', ch_data)
    return (None, None)


while True:
    type, channel_data = V7RC_read()
    if type:
        print(type, channel_data)
    sleep_ms(50)
