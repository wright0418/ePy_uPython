from machine import UART
import ure as re


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
            for name, regex in data_formats:
                ss = re.search(regex, data)
                if ss and name in ('SS8', 'SR2', 'LED', 'LE2'):
                    ch_data = [int(ss.group(0)[i:i+2], 16)
                               for i in range(3, 19, 2)]
                    return (name, ch_data)
                elif ss and name in ('SRT', 'SRV'):
                    print(ss.group(0))
                    ch_data = [int(ss.group(0)[i:i+4])
                               for i in range(3, 19, 4)]
                    return (name, ch_data)
        return (None, None)


if __name__ == '__main__':
    from utime import sleep_ms
    v7rc = V7RC()
    while True:
        type, channel_data = v7rc.read()
        if type:
            print(type, channel_data)
        sleep_ms(50)
