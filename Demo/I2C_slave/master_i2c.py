from machine import I2C, delay, LED
from micropython import const


ACK = const(0xAA)
ShowRGB = const(0x01)
GetButton = const(0x02)


class I2C_BOX():
    def __init__(self, i2c):
        self.i2c_m = i2c

    def show_led(self, R, G, B, slave_addr=0x49):
        """
        Sends a command to the I2C slave to display an RGB color on an LED.
        """
        data = [ShowRGB, R, G, B]
        try:
            rec = self.i2c_m.send(bytearray(data), slave_addr)
            delay(10)
            _ = i2c_m.recv(1, slave_addr)
            delay(10)
        except OSError:
            print("Error sending data to the I2C slave")

    def read_button(self, slave_addr=0x49):
        """
        Sends a command to the I2C slave to read the state of a button.
        Returns True if the button is pressed, False otherwise.
        """
        data = [GetButton, 0, 0, 0]
        try:
            _ = i2c_m.send(bytearray(data), 0x49)
            delay(20)
            Button_state = i2c_m.recv(1, 0x49)
            delay(10)
            if Button_state == b'\x01':
                return True
            elif Button_state == b'\x00':
                return False
        except OSError:
            print("Error sending data to the I2C slave")
            return False


i2c_m = I2C(1, I2C.MASTER, baudrate=400000)
box = I2C_BOX(i2c_m)
status_led = LED('ledy')
status_led.on()

while True:
    for i in range(0, 255, 10):
        box.show_led(R=i, G=100, B=10, slave_addr=0x49)
        delay(100)
        s = box.read_button(slave_addr=0x49)
        print(s)
        delay(100)
