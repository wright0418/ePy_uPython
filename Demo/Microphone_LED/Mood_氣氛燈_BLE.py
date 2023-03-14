from machine import UART
from machine import LED, Switch
from utime import sleep_ms, sleep
from urandom import randrange, randint, uniform
import math
import _thread

# 轉換 HSV 到 RGB


def hsv_to_rgb(h, s, v):
    h_i = int(h*6) % 6
    f = h*6 - h_i
    p = v*(1-s)
    q = v*(1-f*s)
    t = v*(1-(1-f)*s)
    r, g, b = 0, 0, 0
    if h_i == 0:
        r, g, b = v, t, p
    elif h_i == 1:
        r, g, b = q, v, p
    elif h_i == 2:
        r, g, b = p, v, t
    elif h_i == 3:
        r, g, b = p, q, v
    elif h_i == 4:
        r, g, b = t, p, v
    elif h_i == 5:
        r, g, b = v, p, q
    return int(r*255), int(g*255), int(b*255)


def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return int(r*255), int(g*255), int(b*255)


def breath_color(start_color, end_color, steps, duration):
    global should_exit_mode
    """Breathes a color from start_color to end_color over a specified number of steps and duration"""
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color

    for i in range(steps):
        r = int(start_r + (end_r - start_r) * i / steps)
        g = int(start_g + (end_g - start_g) * i / steps)
        b = int(start_b + (end_b - start_b) * i / steps)

        led_color = (r, g, b)
        led.rgb_write([led_color]*LED_NUM)
        sleep(duration / steps)
        if should_exit_mode:
            break


def rainbow_breath(steps, duration):
    global should_exit_mode
    """Displays a rainbow color that fades in and out"""
    while True:
        for i in range(steps):
            r = int((math.sin(i / steps * 2 * math.pi) + 1) * 127.5)
            g = int((math.sin((i / steps + 1/3) * 2 * math.pi) + 1) * 127.5)
            b = int((math.sin((i / steps + 2/3) * 2 * math.pi) + 1) * 127.5)

            breath_color((r, g, b), (0, 0, 0), steps, duration)
            breath_color((0, 0, 0), (r, g, b), steps, duration)
            if should_exit_mode:
                break
            # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break


# 流星燈函数

def meteor_rain(color, tail_length=5, speed=20):
    global should_exit_mode
    led_color = [(0, 0, 0)] * LED_NUM
    for i in range(LED_NUM + tail_length):
        for j in range(tail_length):
            if i - j < LED_NUM and i - j >= 0:
                brightness = (tail_length - j) / tail_length
                led_color[i -
                          j] = tuple(map(lambda x: int(x * brightness), color))
        led.rgb_write(led_color)
        sleep(speed / 1000.0)
        if should_exit_mode:
            break
    led.off()


def meteor_rain_main():
    # 流星燈效果循环
    global should_exit_mode
    color = [RED, GREEN, BLUE, YELLOW, PURPLE, WHITE]
    while True:
        for c in color:
            meteor_rain(c)
            # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break


def calm_show():
    global should_exit_mode
    while True:
        for color in CALM_COLORS:
            for i in range(LED_NUM):
                led_color = [color]*LED_NUM
            led.rgb_write(led_color)
            sleep(1)
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break


# 彩虹流動效果
def marquee():
    global should_exit_mode
    h = 0
    while True:
        led_color = []
        for i in range(LED_NUM):
            r, g, b = hsl_to_rgb(h + i / LED_NUM, 1, 0.5)
            led_color.append((r, g, b))
        led.rgb_write(led_color)
        sleep(0.001)
        h += 0.005
        if h >= 1:
            h = 0
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break

# 爆炸效果


def explosion():
    global should_exit_mode
    while True:
        led_color = [(randrange(0, 256), randrange(0, 256),
                      randrange(0, 256)) for i in range(LED_NUM)]
        led.rgb_write(led_color)
        sleep(0.2)
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break

# 火焰燈


def flame():
    global should_exit_mode
    led_color = [(0, 0, 0)] * LED_NUM
    while True:
        for i in range(LED_NUM):
            r = randint(200, 255)
            g = randint(0, 50)
            b = 0
            led_color[i] = (r, g, b)
        led.rgb_write(led_color)
        sleep(uniform(0.05, 0.1))
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break

# 彩虹漸變效果 - 運動版


def rainbow_movement():
    global should_exit_mode
    leds = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 0, 255), (75, 0, 130), (148, 0, 211)]
    num_leds = len(leds)
    colors = [leds[i % num_leds] for i in range(LED_NUM)]
    h = 0
    while True:
        # 將每個燈的顏色向左移動一個位置
        colors = [colors[(i + 1) % LED_NUM] for i in range(LED_NUM)]
        led.rgb_write(colors)
        sleep(0.05)
        h += uniform(0.005, 0.02)
        if h >= 1:
            h = 0
        # 將新的顏色插入第一個燈，使其保持彩虹漸變的效果
        r, g, b = hsv_to_rgb(h, 1, 1)
        colors[0] = (r, g, b)
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break


# 彩虹漸變效果
def rainbow():
    global should_exit_mode
    h = 0
    while True:
        r, g, b = hsv_to_rgb(h, 1, 1)
        led_color = [(r, g, b)] * LED_NUM
        led.rgb_write(led_color)
        sleep(0.05)
        h += 0.01
        if h >= 1:
            h = 0
        # 如果 should_exit_mode 為 True，則退出當前模式
        if should_exit_mode:
            break


led = LED(LED.RGB)
led.lightness(100)
LED_NUM = 10

# 定义颜色，这里以RGB三原色为例
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

# 稳定平静的心情颜色
CALM_COLORS = [BLUE, CYAN, GREEN]

mode_dict = {
    0: (rainbow_breath, 50, 2),
    1: (meteor_rain_main,),
    2: (calm_show,),
    3: (marquee,),
    4: (explosion,),
    5: (flame,),
    6: (rainbow_movement,),
    7: (rainbow,)
}
should_exit_mode = False


def led_show():
    global should_exit_mode

    while True:
        # 獲取當前模式
        mode = count % len(mode_dict)
        # 獲取當前模式的參數
        params = mode_dict[mode]
        should_exit_mode = False
        # 調用當前模式的函數，如果有參數則傳遞進去
        if len(params) == 1:
            params[0]()
        elif len(params) == 2:
            params[0](params[1])
        elif len(params) == 3:
            params[0](params[1], params[2])


# 創建一個新線程來運行 RGB LED show 函數
_thread.start_new_thread(led_show, ())


def recv_BLE():
    msg = str(ble.readline().strip(b'\x00'), 'utf-8').strip()
    return msg


def key_cb():
    global count, should_exit_mode
    count += 1
    should_exit_mode = True


key = Switch('keya')
key.callback(key_cb)
count = 0
ble = UART(1, 115200, timeout=20)
Y_led = LED('ledy')
G_led = LED('ledg')

G_led.off()
Y_led.on()
while True:
    # add BLE read CMD to change mode
    msg_mode = recv_BLE()
    if msg_mode:
        if msg_mode.isdigit():
            count = int(msg_mode)
            should_exit_mode = True
    sleep_ms(10)
    pass
