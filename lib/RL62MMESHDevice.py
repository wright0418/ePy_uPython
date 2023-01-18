'''
Group ID -- Type
C001 -- LIGHT
C002 -- PLUGA
C003 -- SWITCH
C005 -- EPY
C007 -- FAN

'''
from utime import sleep_ms, ticks_ms, ticks_diff
import ubinascii as binascii


class MeshDevice:

    def __init__(self, uart):

        self.ble = uart
        self.got_flag = False
        self.got_msg = ''
        self.mac_addr = self.MyMac_Addr()

    def __del__(self):
        self.ble.deinit()

    def uart_recv(self):
        timeout = 50
        pre_ticks = ticks_ms()
        while True:
            if self.ble.any():
                try:
                    msg = str(self.ble.readline(), 'utf-8').strip().split(' ')
                    type = msg[0]
                    other = msg[1:]
                    print(type, other)
                    if 'MDTS-MSG' in type or 'MDTGP-MSG' in type:
                        if len(msg) > 2:
                            self.got_flag = True
                            self.got_msg = (msg[1], msg[3])
                            return None, None
                    return type, other
                except:
                    return None, None

            elif ticks_diff(ticks_ms(), pre_ticks) > timeout:
                return None, None
            sleep_ms(10)

    def WriteCMD_withResp(self, atcmd_):
        _ = self.ble.write(atcmd_+'\r\n')
        type, msg = self.uart_recv()
        print(atcmd_)
        return type, msg

    def Re_try_WriteCMD(self, atcmd):
        times = 10
        while times > 0:
            type, m = self.WriteCMD_withResp(atcmd)
            print('===', type, m)
            try:
                if type:
                    if m[0] == "ERROR":
                        times -= 1
                        sleep_ms(1000)
                        continue
                    else:
                        return m[0]  # SUCCESS
            except:
                times -= 1
                sleep_ms(1000)
                continue

    def NodeReset(self):
        self.WriteCMD_withResp('AT+NR')

    def MyMac_Addr(self):
        _, msg = self.WriteCMD_withResp('AT+ADDR')
        print(msg)
        return msg[0][-4:]

    def SendData_Light(self, dst, C=0, W=0, R=0, G=0, B=0):
        msg = self.Re_try_WriteCMD(
            'AT+MDTS 0 0x87F000{}{}070100{:02X}{:02X}{:02X}{:02X}{:02X}'.format(self.mac_addr, dst, C, W, R, G, B))

    def SendData_Switch(self, dst, on_off):
        msg = self.Re_try_WriteCMD(
            'AT+MDTS 0 0x87F000{}{}030200{:02X}'.format(self.mac_addr, dst, on_off))

    def SendData_Fan(self, dst, speed=None, OnOff=None, timer=None, swing=None, mode=None):
        """
        使用查表法去建立傳送的資料與限制
        """
        commands = {
            'speed': (speed, 24, '04040007'),
            'timer': (timer, 8, '04040006'),
            'swing': (swing, None, '04040005'),
            'mode': (mode, None, '04040005'),
            'OnOff': (OnOff, None, '04040001')
        }
        for key, value in commands.items():
            if value[0] is not None:
                if value[1] is not None:
                    if value[0] > value[1]:
                        continue
                msg = self.Re_try_WriteCMD(
                    'AT+MDTS 0 0x87F000{}{}{}{:02X}'.format(self.mac_addr, dst, value[2], value[0]))

    def SendData_EPY(self, dst, send_msg):
        if len(send_msg) > 14:
            send_msg = send_msg[:14]
        length = len(send_msg)
        send_data = str(binascii.hexlify(send_msg), 'utf-8')
        msg = self.Re_try_WriteCMD(
            'AT+MDTS 0 0x87F000{}{}{:02X}{}'.format(self.mac_addr, dst, length, send_data))
        return (msg)

    def ReadMeshMsg(self):
        self.uart_recv()
        if self.got_flag:
            self.got_flag = False
            source = self.got_msg[0]
            msg = self.got_msg[1]
            char_data = str(binascii.unhexlify(msg), 'utf-8')
            return source, char_data
        else:
            return None, None


if __name__ == '__main__':
    from machine import UART
    import gc
    try:
        uart = UART(0, 115200, timeout=20)
    except:
        uart.deinit()
        uart = UART(0, 115200, timeout=20)
    MD = MeshDevice(uart)
    # MD.SendData_Light('C001', 0, 0, 255, 255, 0)
    # MD.SendData_Switch('C002', 1)  # Off
    # MD.SendData_Fan('C007', OnOff=1, swing=1, speed=3, timer=2)
    MD.SendData_EPY('C005', "I am ePy01")

    while True:
        for i in range(0, 256, 32):
            MD.SendData_Light('C001', 0, 0, 0, i, 0)
            sleep_ms(500)
        for i in range(0, 256, 32):
            MD.SendData_Light('C001', 0, 0, i, 0, 0)
            sleep_ms(500)
        for i in range(0, 256, 32):
            MD.SendData_Light('C001', 0, 0, 0, 0, i)
            sleep_ms(500)
        for i in range(0, 256, 32):
            MD.SendData_Light('C001', 0, 0, i, 0, i)
            sleep_ms(500)

    # while True:
    #     source,msg = MD.ReadMeshMsg()
    #     if msg:
    #         print('{} say {}'.format(source,msg))
    #     sleep_ms(1)
