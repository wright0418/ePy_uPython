from machine import LED, Switch, UART, Timer
import ujson as json
import utime
import gc

led = LED(LED.RGB)
rgbdata = [[0, 0, 0]]*400


def tim_cb(t):
    y.toggle()


y = LED('ledy')
g = LED('ledr')

timer = Timer(0, freq=2)
timer.callback(tim_cb)


led.lightness(20)


def show_led_from_file(file_name):
    g.on()
    with open(file_name, 'r') as f:
        ddd = f.read()
        rgbdata = json.loads(ddd)
        del ddd
    try:
        led.rgb_write(rgbdata)

    except:
        pass
    g.off()


def init_ble_centrel():
    uart.write('AT+ROLE=C\r\n')
    uart.readline()
    uart.write('AT+ADV_DATA_SCAN=0\r\n')
    uart.readline()
    uart.write('AT+SCAN_FILTER_NAME=rl\r\n')
    uart.readline()
    uart.write('AT+ADV_DATA_SCAN=1\r\n')
    uart.readline()


def BleAdv_Recv(group='1', mac_addr='7002000005C9'):
    uart.write('AT+ADV_DATA_SCAN=1\r\n')
    utime.sleep(0.05)
    uart.readline()
    if uart.any():
        msg = str(uart.readline(), 'utf-8')
        if ('ADV_DATA ' + mac_addr) in msg and len(msg) == 76:
            recv_data = msg.strip().split(' ')[3][8:]
            gp = int(group)-1
            group_data = recv_data[gp*2:gp*2+2]
            if group_data.isdigit:
                return (chr(int(group_data, 16)))


try:
    uart = UART(1, 115200, timeout=100, read_buf_len=128)
except:
    uart.deinit()
    uart = UART(1, 115200, timeout=100, read_buf_len=128)

init_ble_centrel()

pre_state = 0
new_state = 0
file_list = ['1.txt', '2.txt', '3.txt', '4.txt']
while True:
    for i in range(1, 9):
        file_name = str(i)+'.txt'
        try:
            show_led_from_file(file_name)
        except :
            break
        utime.sleep(0.5)

'''
    ble_data = BleAdv_Recv(group='1', mac_addr='7002000005C9')
    if ble_data:
        try:
            ble_data = int(ble_data)
            if pre_state != ble_data:
                pre_state = ble_data
                # print(ble_data)
                utime.sleep(0.05)
                if 4 >= ble_data >= 1:
                    # show_led_from_file(ble_data)
                    g.on()
                    with open(file_list[ble_data-1], 'r') as f:
                        ddd = f.read()
                        rgbdata = json.loads(ddd)
                        del ddd
                    try:
                        led.rgb_write(rgbdata)

                    except:
                        pass
                    g.off()
            else:
                utime.sleep(0.05)
        except:
            pass
    gc.collect()
    # utime.sleep(0.05)

'''
