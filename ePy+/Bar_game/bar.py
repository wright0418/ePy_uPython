from machine import display as disp
import utime as time

disp.on()

x,y = 0,0
def show_and_run_led():
    global x,y
    disp.set_pixel(x,y,9)
    print (x,y , end ="")
    if x == 0 and y > 0:
        y-=1
    if y == 0 and x <= 6 :
        x+=1
    if x == 7 and y > 6 :
        y -= 1
    if y == 7 and x > 6:
        x -= 1
    if x == 0 and y == 0:
        x=1
    if x == 7 and y ==0:
        y = 1
    if x == 7 and y == 7:
        x = 6
    if x == 0 and y == 7:
        y = 6
    print ('--> ',x,y)
while True:
    show_and_run_led()
    time.sleep(0.1)

