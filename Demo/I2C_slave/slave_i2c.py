from machine import I2C, delay, Switch, LED
from micropython import const

ACK = const(0xAA)
ShowRGB = const(0x01)
GetButton = const(0x02)


class I2C_BOX_slave():
    def __init__(self, i2c, keypad):
        self.i2c_s = i2c
        self.button = keypad
        self.color = (0, 0, 0)

    def process(self):
        recv_data = bytearray(4)
        try:
            recv_data = self.i2c_s.recv(4)
            print(recv_data)
            if recv_data[0] == ShowRGB:
                self.color = (recv_data[1], recv_data[2], recv_data[3])
                print(self.color)
                send_data = ACK
            elif recv_data[0] == GetButton:
                if self.button.value():
                    send_data = b'\x01'
                else:
                    send_data = b'\x00'
            else:
                return
            self.i2c_s.send(send_data)
        except:
            return


i2c_s = I2C(1, I2C.SLAVE, addr=0x49)
keyA = Switch('keya')
led = LED(LED.RGB)
box_slave = I2C_BOX_slave(i2c_s, keyA)


while True:
    box_slave.process()
    led.rgb_write(1, *box_slave.color)
