import math
import utime as time
from machine import LED, ADC, Pin


def log10(x):
    return math.log(x) / math.log(10)
# 初始化 RGB LED


# 設定音量閥值
V_REF = 50
NUM_LED = 12
led = LED(LED.RGB)
np = [[0, 0, 0]]*NUM_LED
# 初始化 ADC
adc = ADC(Pin.epy.AIN1)

# 初始化 EMA 参数
ALPHA = 0.2
ema_prev = 0.0
ema_curr = 0

# 记录环境噪声水平的RMS值
background_rms = 0.0

# 计算EMA参数动态调整的参数K
K = 0.5

# 將EMA計算和LED顯示寫成兩個函數


def calc_rms(ema_curr, data):
    ema_curr = ALPHA * data + (1 - ALPHA) * ema_curr
    rms = math.sqrt(ema_curr)

    return ema_curr, rms


def display_led(rms):
    rms = min(rms, V_REF)
    rms_norm = rms / V_REF
    num_led_on = round(rms_norm * NUM_LED)
    for i in range(num_led_on):
        r = round((1 - i / NUM_LED) * 255)
        g = round((i / NUM_LED) * 255)
        np[i] = (r, g, 0)
    for i in range(num_led_on, NUM_LED):
        np[i] = (0, 0, 0)
    led.rgb_write(np)


# 主要程式碼
while True:
    # 讀取ADC數值
    data = adc.read()

    # 計算RMS
    ema_curr, rms = calc_rms(ema_curr, data)

    # 顯示LED
    display_led(rms)
