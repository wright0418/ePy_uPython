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


def show_led_from_file(file_index):
    g.on()
    with open(file_list[file_index-1], 'r') as f:
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
    utime.sleep(0.2)
    _ = uart.read(uart.any())
    uart.write('AT+ADV_DATA_SCAN=0\r\n')
    uart.readline()
    uart.write('AT+SCAN_FILTER_NAME=rl\r\n')
    uart.readline()
    uart.write('AT+SCAN_INTERVAL=10\r\n')
    uart.readline()
    uart.write('AT+SCAN_WINDOW=10\r\n')
    uart.readline()


def BleAdv_Recv(group='1', mac_addr='7002000005C9'):
    uart.write('AT+ADV_DATA_SCAN=1\r\n')
    uart.readline()
    msg = str(uart.readline(), 'utf-8')
    if msg:
        if ('ADV_DATA ' + mac_addr) in msg and len(msg) == 76:

            recv_data = msg.strip().split(' ')[3][8:]
            gp = int(group)-1
            group_data = recv_data[gp*2:gp*2+2]
            if group_data.isdigit:
                uart.write('AT+ADV_DATA_SCAN=0\r\n')
                uart.readline()
                try:
                    return (chr(int(group_data, 16)))
                except:
                    pass
    uart.write('AT+ADV_DATA_SCAN=0\r\n')
    uart.readline()


try:
    uart = UART(1, 115200, timeout=100, read_buf_len=128)
except:
    uart.deinit()
    uart = UART(1, 115200, timeout=100, read_buf_len=128)

init_ble_centrel()


pre_state = 0
new_state = 0
file_list = ['epy.txt', 'gmail.txt', 'python.txt', 'cloudy.txt']

# recv_mac = '7002000005C9'
recv_mac = '700200000339'
while True:
    ble_data = BleAdv_Recv(group='1', mac_addr=recv_mac)
    if ble_data:
        try:
            ble_data = int(ble_data)
            if pre_state != ble_data:
                pre_state = ble_data
                print(ble_data)
                # utime.sleep(0.05)  # 讓自動整理一下記憶體 (BleAdv_Recv使用了許多記憶體)
                # if 4 >= ble_data >= 1:
                #     # show_led_from_file(ble_data)
                #     g.on()
                #     with open(file_list[ble_data-1], 'r') as f:
                #         ddd = f.read()
                #         rgbdata = json.loads(ddd)
                #         del ddd
                #     try:
                #         led.rgb_write(rgbdata)

                #     except:
                #         pass
                #     g.off()
            else:
                utime.sleep(0.05)
        except:
            pass
    gc.collect()
    # utime.sleep(0.05)
