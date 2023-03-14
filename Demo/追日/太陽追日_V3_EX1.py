from machine import ADC, Servo, Pin, Switch, LED
import utime as time
H_servo = Servo(1)
V_servo = Servo(2)
'''
Sensor 面相太陽能的方位
'''
sensor_R_U = ADC(Pin.epy.AIN1)
sensor_L_U = ADC(Pin.epy.AIN0)
sensor_R_D = ADC(Pin.epy.AIN5)
sensor_L_D = ADC(Pin.epy.AIN2)

Key = Switch('keya')
led = LED('ledy')

now_H_angle = 90
now_V_angle = 90

# 0 is False (光) ,1 is  True

Cab = 280/180
mode_th = {'indoor': 1000, 'outdoor': 4050}
Th = mode_th['indoor']

key_state = False


def key_cb():
    global key_state
    key_state = not key_state


def Read_sensor():

    _ru_data = sensor_R_U.read()
    time.sleep_ms(1)
    _rd_data = sensor_R_D.read()
    time.sleep_ms(1)
    _ld_data = sensor_L_D.read()
    time.sleep_ms(1)
    _lu_data = sensor_L_U.read()
    #print(_ru_data, _rd_data, _ld_data, _lu_data)
    return (_ru_data, _rd_data, _ld_data, _lu_data)


def Motor_Ctrl(H_move, V_move):

    global now_H_angle, now_V_angle
    #print('V = ', V_move)
    if now_H_angle <= 180 or now_H_angle >= 0:
        now_H_angle += H_move
    if now_V_angle <= 180 or now_V_angle >= 60:
        now_V_angle += V_move

    H_servo.angle(int(now_H_angle * Cab))
    V_servo.angle(int(now_V_angle * Cab))


Motor_Ctrl(0, 0)
Key.callback(key_cb)
time.sleep(1)

while True:

    if key_state:
        Th = mode_th['outdoor']
        led.on()
    else:
        Th = mode_th['indoor']
        led.off()

    (RU, RD, LD, LU) = Read_sensor()
    #print(RU, RD, LU, LD)

    if RU > Th and LU > Th:
        Motor_Ctrl(0, -1)
    if RU > Th and RD > Th:
        Motor_Ctrl(+1, 0)
    if RU > Th and RD < Th and LU < Th and LD < Th:
        Motor_Ctrl(+1, -1)
    if LU > Th and LD > Th:
        Motor_Ctrl(-1, 0)
    if LD > Th and RU < Th and LU < Th and RD < Th:
        Motor_Ctrl(-1, +1)
    if LD > Th and RD > Th:
        Motor_Ctrl(0, +1)
    if RD > Th and RU < Th and LU < Th and LD < Th:
        Motor_Ctrl(+1, +1)
    if LU > Th and RU < Th and LD < Th and RD < Th:
        Motor_Ctrl(-1, -1)
    time.sleep_ms(10)
