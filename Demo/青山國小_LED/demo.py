from machine import LED, Switch, UART, Timer
import ujson as json
import utime as time
import gc

led = LED(LED.RGB)

y = LED('ledy')
g = LED('ledr')


def tim_cb(t):
    y.toggle()


# Live 指示system is living
timer = Timer(0, freq=2)
timer.callback(tim_cb)
led.lightness(100)


def init_ble_centrel():
    uart.write('AT+ROLE=C\r\n')
    uart.readline()
    uart.write('AT+ADV_DATA_SCAN=0\r\n')
    uart.readline()
    uart.write('AT+SCAN_FILTER_NAME=rl\r\n')
    uart.readline()
    uart.write('AT+ADV_DATA_SCAN=1\r\n')
    uart.readline()


def BleAdv_Recv(group='1', mac_addr='70300000F00C'):
    uart.write('AT+ADV_DATA_SCAN=1\r\n')
    uart.readline()
    time.sleep(0.1)

    if uart.any():
        msg = str(uart.readline(), 'utf-8')
        if ('ADV_DATA ' + mac_addr) in msg and len(msg) == 76:
            recv_data = msg.strip().split(' ')[3][8:]
            gp = int(group)-1
            group_data = recv_data[gp*2:gp*2+2]
            if group_data.isdigit:
                return (chr(int(group_data, 16)))


def hsv_to_rgb(h, s, v):
    h = h % 360
    hi = int(h / 60) % 6
    f = h / 60 - hi
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    rgb = [(v, t, p), (q, v, p), (p, v, t),
           (p, q, v), (t, p, v), (v, p, q)][hi]
    return tuple(int(x * 255) for x in rgb)


def rainbow(num_leds, hue_step, saturation, value):
    hue = 0
    rainbow = []
    for i in range(num_leds):
        hue = (hue + hue_step) % 360
        rainbow.append(hsv_to_rgb(hue, saturation, value))
    return rainbow


def roll_rainbow(rainbow, num_leds, direction):
    if direction == "forward":
        rolled = rainbow[1:] + [rainbow[0]]
    else:
        rolled = [rainbow[-1]] + rainbow[:-1]
    return rolled


led_data = [[0, 0, 0]]*100
first_list = [13, 19, 48, 54, 57, 60, 66, 69, 72, 75, 81, 84, 87, 90, 29, 32]


def light_first():
    # led_data = [[0, 0, 0]]*100
    for start in first_list:
        led_data[start] = [255, 0, 255]
        led_data[start] = [255, 0, 255]
        led_data[start] = [255, 0, 255]
    led.rgb_write(led_data)


def light_all():
    led_data = [[255, 0, 255]]*100
    led.rgb_write(led_data)


def off_all():
    led_data = [[0, 0, 0]]*100
    led.rgb_write(led_data)


try:
    uart = UART(1, 115200, timeout=100, read_buf_len=128)
except:
    uart.deinit()
    uart = UART(1, 115200, timeout=100, read_buf_len=128)

# 初始化 BLE to Centrel Mode (接收廣播)
init_ble_centrel()


num_leds = 100
hue_step = 360 / num_leds
saturation = 1.0
value = 1.0
direction = "forward"
pre_state = 0
new_state = 0

Adv_mac_addr = '70300000F00C'


for i in range(3):
    off_all()
    time.sleep(0.5)
    light_first()
    time.sleep(0.5)
off_all()
while True:
    ble_data = BleAdv_Recv(group='1', mac_addr='70300000F00C')
    if ble_data == "1":

        for i in range(5):
            off_all()
            time.sleep(0.5)
            light_first()
            time.sleep(0.5)

        for i in range(5):
            off_all()
            time.sleep(0.5)
            light_all()
            time.sleep(0.5)

        rainbow = rainbow(num_leds, hue_step, saturation, value)
        while True:
            rainbow = roll_rainbow(rainbow, num_leds, direction)
            led.rgb_write(rainbow)
            time.sleep(0.01)
    print('--', ble_data)
    time.sleep(0.05)
