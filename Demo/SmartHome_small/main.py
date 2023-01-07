from machine import LED, ADC, UART, Pin, I2C, Timer, RTC, PWM
from ePy4Digit import FourDigit
from htu21d import HTU21D
import utime as time
import RL62M
import gc

rtc = RTC()
rtc.datetime((2022, 11, 12, 3, 7, 2, 59, 0))
_debug = True
sys_module = "S1"
FW_version = "0.0.1"

rgbled = LED(LED.RGB)
ledy = LED('ledy')
ledr = LED('ledr')
ledg = LED('ledg')
rgbled.lightness(100)

LIGHT_upTH = 1000
LIGHT_downTH = 300
TEMPER_TH = 27


class Tone:
    def __init__(self, pin, timer_ch):
        self._buzzer_pin = Pin(pin, Pin.OUT)
        self._timer = timer_ch

    def timer_ISR(self, t):
        self._buzzer_pin.value(~self._buzzer_pin.value() & 0x0001)

    def play_freq(self, freq, period_ms):
        self._timer.init(freq=freq*2)
        self._timer.callback(self.timer_ISR)
        time.sleep_ms(int(period_ms))
        self._timer.callback(None)


class Motor:
    def __init__(slef, pinA, pinB):
        slef.pwma = PWM(pinA, freq=10000, duty=0)
        slef.pwmb = PWM(pinB, freq=10000, duty=0)

    def CC(slef, speed):
        slef.pwma.duty(speed)
        slef.pwmb.duty(0)

    def CW(slef, speed):
        slef.pwma.duty(0)
        slef.pwmb.duty(speed)

    def Stop(slef):
        slef.pwma.duty(0)
        slef.pwmb.duty(0)


'''
when active_level is "Low" KeyPad.state = True 
'''


class KeyPad:
    def __init__(self, pin, active_level="Low"):
        self.pin = Pin(pin, Pin.IN)
        self.state = False  # Key Press "True"
        self.act_level = active_level
        pin.irq(handler=self.keyPad_ISR,
                trigger=self.pin.IRQ_FALLING | self.pin.IRQ_RISING)

    def keyPad_ISR(self, pin_):

        if self.act_level == "Low":
            self.state = False if self.pin.value() else True
        else:
            self.state = True if self.pin.value() else False


class ADCSensor():
    def __init__(self, adc_pin):
        self.adc = ADC(adc_pin)

    def read(self):
        return (self.adc.read())


def ring(times):
    for i in range(times):
        tone.play_freq(988, 200)
        tone.play_freq(784, 700)
        time.sleep(0.5)


def police_sound():
    for freq in range(650, 1450, 10):
        tone.play_freq(freq, 10)
    for freq in range(1550, 750, -10):
        tone.play_freq(freq, 10)


def flash_led():
    for n in range(1, 6):
        rgbled.rgb_write(n, 255, 0, 0)
    time.sleep(0.2)
    rgbled.off()
    time.sleep(0.1)


def AllLed_On():
    for n in range(1, 6):
        rgbled.rgb_write(n, 255, 255, 255)


def disp_show():
    global loop_index, temper, humi, disp_loop
    loop_index += 1
    index = loop_index//20

    if loop_index >= (3*20):
        loop_index = 0
        return

    if disp_loop[index] == 'time':
        four_digi.show_time(rtc.datetime()[4], rtc.datetime()[5])
        # four_digi.show_time(rtc.datetime()[4], rtc.datetime()[6])  # show sec for test
    elif disp_loop[index] == 'temper':
        four_digi.show_temper(sensor.readTemperatureData())
    elif disp_loop[index] == 'humi':
        four_digi.show4number(sensor.readHumidityData())


def Ble_task():

    BLEData = BLE.RecvData()

    if BLE.state != 'CONNECTED' or BLEData == '':
        return
    data = BLEData.split(',')

    if len(data) >= 2:
        now = list(rtc.datetime())
        if 'Hour' in data[0] and data[1].isdigit:
            now[4] = int(data[1])
        elif 'Min' in data[0] and data[1].isdigit:
            now[5] = int(data[1])
        rtc.datetime(tuple(now))


''' IO define 
'''
door_key = KeyPad(Pin.epy.P6, active_level="High")  # Active "H"
window_alarm = KeyPad(Pin.epy.P7, active_level="High")
light_input = ADCSensor(Pin.epy.AIN0)
fan = Motor(Pin.epy.PWM2, Pin.epy.PWM3)

tim = Timer(0)
tone = Tone(Pin.epy.P9, tim)

i2c1 = I2C(1, I2C.MASTER, baudrate=100000)
four_digi = FourDigit(i2c1)
i2c0 = I2C(0, I2C.MASTER, baudrate=100000)
sensor = HTU21D(i2c0)


ble1 = UART(1, 115200, timeout=20, read_buf_len=64)
BLE = RL62M.GATT(ble1)


disp_loop = ["time", "temper", "humi"]
loop_index = 0

while True:
    disp_show()
    Ble_task()
    while window_alarm.state:
        police_sound()
        flash_led()

    if door_key.state:
        ring(3)

    if light_input.read() < LIGHT_downTH:
        AllLed_On()
    elif light_input.read() >= LIGHT_upTH:
        rgbled.off()

    now_temper = sensor.readTemperatureData()
    if now_temper >= TEMPER_TH:
        fan.CW(100)
    else:
        fan.Stop()

    gc.collect()
    time.sleep(0.1)
