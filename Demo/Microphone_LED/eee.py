import math
import utime as time
from machine import LED, ADC, Pin


def log10(x):
    return math.log(x) / math.log(10)


# 初始化 RGB LED
NUM_LED = 10
led = LED(LED.RGB)
np = [[0, 0, 0]]*NUM_LED

# 設定音量閥值
V_REF = 50

# 初始化 ADC
adc = ADC(Pin.epy.AIN1)

# 初始化 EMA 参数
ALPHA = 0.2
SILENCE_THRESHOLD = 0.05
ema_prev = 0.0
ema_curr = 0
background_noise = 0

# 將EMA計算和LED顯示寫成兩個函數


def calc_rms(data):
    global ema_curr, ema_prev
    ema_curr = ALPHA * data + (1 - ALPHA) * ema_prev
    ema_prev = ema_curr
    try:
        rms = math.sqrt(ema_curr - background_noise)
    except:
        rms = 0
    return rms


def display_led(rms):
    rms = min(rms, V_REF)
    rms_norm = rms / V_REF
    num_led_on = round(rms_norm * NUM_LED)
    num_led_on = min(num_led_on, NUM_LED)
    for i in range(num_led_on):
        g = round((1 - i / NUM_LED) * 255)
        r = round((i / NUM_LED) * 255)
        np[i] = (r, g, 0)
    for i in range(num_led_on, NUM_LED):
        np[i] = (0, 0, 0)
    led.rgb_write(np)


# 主要程式碼
while True:
    # 保持安靜 2 秒
    time.sleep(2)

    # 計算背景噪音
    print('Please keep quiet')
    background_noise = 0
    for i in range(100):
        background_noise += adc.read()
    background_noise /= 100
    ema_prev = background_noise
    print('Background noise:', background_noise)

    # 顯示開始監聽的提示
    print('Start listening')

    # 監聽聲音並顯示
    while True:
        data = adc.read()
        rms = calc_rms(data)
        display_led(rms)
