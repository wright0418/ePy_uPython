from machine import I2C
from machine import UART, LED, Pin
import utime as time


'''
key1--AIN1 ,key2--AIN2 ,key3--AIN3 ,key4--AIN4 ,key5--AIN5

'''
now_key = None
# from ePy4Digit import FourDigit
# i2c1 = I2C(1, I2C.MASTER, baudrate=100000)
# Seg7Addr = 0x3D
# four_digi = FourDigit(i2c1)


def key_cb(pin):
    global now_key
    if pin == key1:
        now_key = 1
    elif pin == key2:
        now_key = 2
    elif pin == key3:
        now_key = 3
    elif pin == key4:
        now_key = 4

    print(now_key)


uart = UART(1, 115200, timeout=20)
y = LED('ledy')
r = LED('ledr')

key1 = Pin(Pin.epy.P24, Pin.IN)
key2 = Pin(Pin.epy.P6, Pin.IN)
key3 = Pin(Pin.epy.P7, Pin.IN)
key4 = Pin(Pin.epy.P8, Pin.IN)


key1.irq(handler=key_cb, trigger=key1.IRQ_FALLING)
key2.irq(handler=key_cb, trigger=key2.IRQ_FALLING)
key3.irq(handler=key_cb, trigger=key3.IRQ_FALLING)
key4.irq(handler=key_cb, trigger=key4.IRQ_FALLING)


def sendAdvData(_times):
    if 9 < _times < 0:
        return
    data = hex(ord(str(_times)))[2:]
    sendData = "AT+AD_SET=0,1709726C{}31313204050607080911223344556677889944\r\n".format(
        data)
    _ = uart.write(sendData)
    time.sleep_ms(20)


pre_key = None

show_no = 0

sendData ="AT+ADVERT=0\r\n" 
_ = uart.write(sendData)
r = uart.readline()


sendData ="AT+ADV_INTERVAL=50\r\n" 
_ = uart.write(sendData)
r = uart.readline()


sendData ="AT+ADVERT=1\r\n" 
_ = uart.write(sendData)
r = uart.readline()


while True:
    for key in range(1, 5):
        sendAdvData(key)
        time.sleep(0.5)

    # if now_key != pre_key:
    #     sendAdvData(now_key)
    #     # four_digi.show4number(now_key)
    #     y.toggle()
    #     pre_key = now_key
    # time.sleep(0.01)
