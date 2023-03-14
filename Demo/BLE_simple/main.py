from machine import UART, delay, LED


def init_BLE():
    # RL62M01 change to CMD mode
    ble.write('!CCMD@')
    delay(150)
    # enable BLE System MSG
    ble.write('AT+EN_SYSMSG=1\r\n')
    delay(50)
    ble.read(ble.any())  # clear UART buffer


# Lite BLE on UART port 1, baudrate is 115200)
ble = UART(1, 115200, timeout=100)
init_BLE()
ledy = LED('ledy')
ledr = LED('ledr')

while True:
    msg = ble.readline()

    recv_data = str(msg, 'utf-8')
    # clear 'x\00' data
    recv_data = recv_data.replace('x\00', '')
    # strip \n
    recv_data = recv_data.strip()

    # check data
    if recv_data:
        if recv_data == 'A':
            ledy.toggle()
        if recv_data == 'B':
            ledr.toggle()
        if recv_data == 'b':
            ledr.toggle()
