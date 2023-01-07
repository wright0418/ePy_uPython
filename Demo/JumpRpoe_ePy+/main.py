'''
V1.1
- fixed BLE send times issues 
'''
from machine import accelerometer as axl
from machine import display
from machine import Pin, UART, LED
import utime
import music
import RL62M
import gc


def CorrectionAcc():
    x_ = []
    y_ = []
    z_ = []
    for i in range(50):
        x_.append(axl.get_x())
        y_.append(axl.get_y())
        z_.append(axl.get_z())
        if i % 10 == 0:
            music.play(['C:1'], wait=True)
            utime.sleep_ms(50)
    xAvg = sum(x_)/len(x_)
    yAvg = sum(y_)/len(y_)
    zAvg = sum(z_)/len(z_)
    if _debug:
        print(x_, y_, z_)
        print("x_avg=", xAvg, "y_avg=", yAvg, "z_avg=", zAvg)
    return xAvg, yAvg, zAvg


_debug = False

zUpCritacal = 700  # 800
zDownCritacal = -1500
x_avg = y_avg = z_avg = 0
z_flag = 1

start_key = Pin(Pin.epy.KEYA, Pin.IN)
end_key = Pin(Pin.epy.KEYD, Pin.IN)
BLEuart = UART(1, 115200)
ledy = LED('ledy')
ledg = LED('ledg')
ledr = LED('ledr')
BLE = RL62M.GATT(BLEuart)


Count_JumpRope = Count_P = Count_N = speed = 0
game_state = 'STOP'
'''main '''

ledg.off()
ledr.off()
ledy.off()

x_avg, y_avg, z_avg = CorrectionAcc()
if z_avg < 0:
    z_flag = 1
else:
    z_flag = 0

ledy.on()
while True:
    recv_msg = BLE.RecvData()

    if BLE.state == 'CONNECTED':
        ledr.off()
        ledg.on()
        if recv_msg != '' and recv_msg != '\x00':
            if _debug:
                print('BLE_recv=>', recv_msg)
            recv_msg = recv_msg.split(',')
            if recv_msg[1] == 'conn st':
                pass
            elif recv_msg[1] == 'get cycle':
                sendData = 'send,{}\n'.format(0)
                BLE.SendData(sendData)
                music.play(['A:8'], wait=True)
                Count_JumpRope = Count_P = Count_N = speed = 0
                game_state = 'START'

            elif recv_msg[1] == 'set end':
                game_state = 'STOP'
                display.on()
                display.scroll(Count_JumpRope, delay=300, wait=False)
                music.play(['B:1', 'A', 'F', 'E', 'D', 'C'], wait=True)

            elif recv_msg[1] == 'disc':
                game_state = 'STOP'
                BLE.disconnect()

        if game_state == 'START':
            x = axl.get_x()-x_avg
            y = axl.get_y()-y_avg
            z = axl.get_z()-z_avg

            if z_flag == 1:
                z = z*-1
            if z > zUpCritacal:  # 800
                if _debug:
                    print('+', end='')
                Count_P = 1
                Count_N = 0
            elif z < zDownCritacal:  # 1500
                if _debug:
                    print('-', end='')
                Count_N = 1
            else:
                if _debug:
                    print('z =', z)

            if Count_P == 1:
                speed += 1
                if Count_N == 1:
                    if speed < 15:  # 15
                        Count_JumpRope += 1
                        Count_P = Count_N = speed = 0
                        #music.play(['C:1'], wait=False)

                elif speed > 15:
                    Count_P = Count_N = speed = 0
            sendData = 'send,{}\n'.format(Count_JumpRope)
            BLE.SendData(sendData)
    else:
        Count_JumpRope = Count_P = Count_N = speed = 0
        ledr.on()
        ledg.off()
    # if _debug:
    #     if gc.mem_free() < 100:
    #         print('free_mem = ', gc.mem_free())
    ledy.toggle()
    utime.sleep(0.03)
