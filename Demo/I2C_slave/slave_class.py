from machine import I2C, Switch, LED
from micropython import const

# Define a constant value for ACK response
ACK = const(0xAA)


class I2C_BOX_slave():
    def __init__(self, i2c):
        self.i2c_s = i2c
        self.handlers = {}

    def register_handler(self, command, handler):
        # Add a handler function for a given command
        self.handlers[command] = handler

    def process(self):
        recv_data = bytearray(4)
        try:
            # Receive data from the master device
            recv_data = self.i2c_s.recv(4)
            # The first byte is the command, so extract it
            command = recv_data[0]
            # Extract the data portion of the received message
            recv_data = recv_data[1:]
            print(command, recv_data)
            # If the command has a handler function, call it with the received data
            if command in self.handlers:
                send_data = self.handlers[command](recv_data)
            else:
                return

            # If the handler returns an integer, convert it to a bytes object
            if isinstance(send_data, int):
                send_data = bytes([send_data])
            # Send the response back to the master device
            self.i2c_s.send(send_data)
        except:
            return


def show_rgb_handler(data):
    print('show_rgb_handler', data)
    # Call the LED's RGB write function with the received data
    led.rgb_write(1, data[0], data[1], data[2])
    # Return the ACK response
    return ACK


def get_button_handler(data):
    print('get_button_handler', data)
    # Return the state of the button on the slave device
    if keyA.button.value():
        return b'\x01'
    else:
        return b'\x00'


# Create an I2C slave device with the specified address
i2c_s = I2C(1, I2C.SLAVE, addr=0x49)
# Create a Switch object for the keyA button
keyA = Switch('keya')
# Create an LED object for the RGB LED
led = LED(LED.RGB)
# Create a new I2C_BOX_slave object with the I2C and Switch objects
box_slave = I2C_BOX_slave(i2c_s, keyA)
# Register the handler functions for the corresponding commands
box_slave.register_handler(0x01, show_rgb_handler)
box_slave.register_handler(0x02, get_button_handler)

# Continuously process incoming messages
while True:
    box_slave.process()
