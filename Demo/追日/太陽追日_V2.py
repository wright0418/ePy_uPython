from machine import ADC, Servo, Pin
import utime as time
H_servo = Servo(1)
V_servo = Servo(2)
sensor_L_D = ADC(Pin.epy.AIN0)
sensor_R_D = ADC(Pin.epy.AIN1)
sensor_R_U = ADC(Pin.epy.AIN2)
sensor_L_U = ADC(Pin.epy.AIN3)

now_H_angle = 90
now_V_angle = 90

# 0 is False (光) ,1 is  True
Cab = 280/180

def Read_sensor():
    _ru_data = sensor_R_U.read()
    time.sleep_ms(1)
    _rd_data = sensor_R_D.read()
    time.sleep_ms(1)
    _ld_data = sensor_L_D.read()
    time.sleep_ms(1)
    _lu_data = sensor_L_U.read()
    #print(_ru_data//3000, _rd_data//3000, _ld_data//3000, _lu_data//3000)
    return bool(_ru_data//3000), bool(_rd_data//3000), bool(_ld_data//3000), bool(_lu_data//3000)


def Motor_Ctrl(H_move, V_move):
    global now_H_angle, now_V_angle
    print ('V = ',V_move)
    if now_H_angle != 180 or now_H_angle != 0:
        now_H_angle += H_move
    if now_V_angle != 180 or now_V_angle != 0:
        now_V_angle += V_move
        
    H_servo.angle(int(now_H_angle * Cab))
    V_servo.angle(int(now_V_angle * Cab))


# ru,rd,ld,lu
move_table = {(False, False, False, False): [0, 0], (False, False, False, True): [+1, -1], (False, False, True, False): [+1, +1], (False, False, True, True): [+1, 0],
              (True, False, False, False): [-1, -1], (True, False, False, True): [0, -1], (True, False, True, False): [0, 0], (True, False, True, True): [+1, -1],
              (False, True, False, False): [-1, +1], (False, True, False, True): [0, 0], (False, True, True, False): [0, +1], (False, True, True, True): [+1, +1],
              (True, True, False, False): [-1, 0], (True, True, False, True): [-1, -1], (True, True, True, False): [-1, +1], (True, True, True, True): [0, 0]}


while True:
    light_state = Read_sensor()
    # print(light_state)
    Motor_Ctrl(move_table[light_state][0], move_table[light_state][1])
