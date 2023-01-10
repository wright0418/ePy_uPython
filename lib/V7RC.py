from machine import UART
import ure as re
from utime import sleep_ms
try:
    ble = UART(1, 115200, timeout=100, read_buf_len=64)
except:
    ble.deinit()
    ble = UART(1, 115200, timeout=20, read_buf_len=64)


def V7RC_read():
    data = ble.readline()
    if data != b'':
        ss = re.search(r'#SRT[0-9]*?#', data)
        if ss:
            return ('SRT', int(ss.group(0)[4:8]), int(ss.group(0)[8:12]), int(ss.group(0)[12:16]), int(ss.group(0)[16:20]))
        ss = re.search(r'#SRV[0-9]*?#', data)
        if ss:
            return ('SRV', int(ss.group(0)[4:8]), int(ss.group(0)[8:12]), int(ss.group(0)[12:16]), int(ss.group(0)[16:20]))

    return (None, None)


while True:
    type, *data = V7RC_read()
    if type:
        print(type, data)
    sleep_ms(100)
