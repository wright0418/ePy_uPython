
import utime
from machine import LED

y = LED('ledy')
y.on()
while True:
    msg = input()
    if msg:
        with open('ttt.txt', 'a') as f:
            f.write(msg)
    utime.sleep(0.3)
