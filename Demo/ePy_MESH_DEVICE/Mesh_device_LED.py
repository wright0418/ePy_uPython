from machine import UART, LED
from utime import sleep

try:
    uart = UART(1, 115200, timeout=200)
except:
    uart.deinit()
    uart = UART(1, 115200, timeout=200)


def Mesh_AT_CMD(cmd):
    _ = uart.read(uart.any())
    _ = uart.write('AT+{}\r\n'.format(cmd))


def Mesh_read():
    global my_uid, my_prov_state, publish_from, publish_data, publish_updated, my_data, data_updated
    msg = str(uart.readline(), 'utf-8').strip()
    if msg:
        # print(msg)
        msg = msg.split(' ')
        if 'SYS-MSG' in msg[0] and len(msg) >= 3:
            if msg[1] == 'DEVICE':
                if len(msg) >= 4:
                    my_uid = msg[3]
                    my_prov_state = msg[2]
                else:
                    my_prov_state = msg[2]
        if 'PROV-MSG' in msg[0] and len(msg) == 3:
            if msg[1] == 'SUCCESS':
                my_prov_state = 'PROV-ED'
                my_uid = msg[2]
            else:
                my_prov_state = 'UNPROV'
        if 'MDTGP-MSG' in msg[0] and len(msg) == 4:
            publish_from = msg[1]
            publish_data = msg[3]
            publish_updated = True
        if 'MDTS-MSG' in msg[0] and len(msg) == 4:
            my_data = msg[3]
            data_updated = True
    else:
        return


def check_piblish():
    global my_uid, my_prov_state, publish_from, publish_data, publish_updated
    if publish_updated:
        if publish_data == 'FF':
            G_LED.on()
            Y_LED.on()
            R_LED.on()
        elif publish_data == '00':
            G_LED.off()
            Y_LED.off()
            R_LED.off()
        publish_updated = False


def check_prov_state():
    global my_prov_state
    if my_prov_state != 'PROV-ED':
        G_LED.toggle()


def check_my_data():
    global my_data, data_updated
    if data_updated:
        if my_data == '01':
            G_LED.on()
        elif my_data == '02':
            G_LED.off()
        elif my_data == '03':
            Y_LED.on()
        elif my_data == '04':
            Y_LED.off()
        elif my_data == '05':
            R_LED.on()
        elif my_data == '06':
            R_LED.off()
        data_updated = False


def change_my_data(data):
    '''
    data = 'FF' / '00' 
    '''
    uart.write('AT+MDTS 0 x{}\r\n'.format(data))


my_uid = None
my_data = None
data_updated = False
my_prov_state = None
publish_from = None
publish_data = None
publish_updated = False


G_LED = LED('ledg')
Y_LED = LED('ledy')
R_LED = LED('ledr')

button_send_data = "FF"

Mesh_AT_CMD('REBOOT')  # reboot RL62M02 Device module to get the prov_status
while True:
    Mesh_read()
    check_prov_state()
    check_piblish()
    check_my_data()
