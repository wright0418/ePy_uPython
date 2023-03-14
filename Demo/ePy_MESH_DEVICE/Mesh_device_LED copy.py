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


def read_msg(msg):
    msg = msg.split(' ')
    return msg[0], msg[1:]


def handle_sys_msg(data):
    # 處理 SYS-MSG 訊息的函式
    global my_uid, my_prov_state
    if data[0] == 'DEVICE':
        my_uid = data[3] if len(data) >= 3 else ''
        my_prov_state = data[2]


def handle_prov_msg(data):
    global my_prov_state, my_uid
    # 處理 PROV-MSG 訊息的函式
    my_prov_state = 'PROV-ED' if data[0] == 'SUCCESS' else 'UNPROV'
    my_uid = data[1]


def handle_mdtgp_msg(data):
    # 處理 MDTGP-MSG 訊息的函式
    global publish_data, publish_from, publish_updated
    publish_from = data[0]
    publish_data = data[2]
    publish_updated = True
    pass


def handle_mdts_msg(data):
    global my_data, data_updated
    # 處理 MDTS-MSG 訊息的函式
    my_data = data[3]
    data_updated = True
    pass


msg_handlers = {
    'SYS-MSG': handle_sys_msg,
    'PROV-MSG': handle_prov_msg,
    'MDTGP-MSG': handle_mdtgp_msg,
    'MDTS-MSG': handle_mdts_msg
}


def Mesh_read():
    global my_uid, my_prov_state, publish_from, publish_data, publish_updated, my_data, data_updated
    data = str(uart.readline(), 'utf-8').strip()
    if data:
        msg_type, msg_data = read_msg(data)
        if msg_type in msg_handlers:
            msg_handlers[msg_type](msg_data)
        else:
            print(f"Unknown message type: {msg_type}")


def check_publish():
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
        LED_dict = {
            '01': G_LED.on,
            '02': G_LED.off,
            '03': Y_LED.on,
            '04': Y_LED.off,
            '05': R_LED.on,
            '06': R_LED.off
        }
        LED_dict[my_data]()
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
    check_publish()
    check_my_data()
    sleep(0.2)
