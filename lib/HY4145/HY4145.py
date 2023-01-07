"""
 ePy-Lite_HY4145.py

 ePy-Lite  HY4145
 ------------
 VIN       Peak+
 P17       SCL
 P16       SDA
 GND       Peak-
"""

from machine import I2C,delay, Pin
from machine import Switch   #Get button KEY library
from machine import Timer
import Hygauge

temp = None
Volt = None
tim_3 = None
TimerDone = None
KeyDone = None

def key_int():
  global KeyDone
  KeyDone = True

def tick3(timer):
  global TimerDone
  TimerDone = True

# Start Function
if __name__=="__main__":
  KeyA = Switch('keya')    #Create button A
  KeyA.callback(key_int)
  KeyDone = False

  tim_3 = Timer(3,freq = 1)
  tim_3.callback(tick3)
  TimerDone = False

  # Declaration I2C
  i2c_0 = I2C(0,I2C.MASTER,baudrate=400000)      #Create I2C0 Master Mode, Baudrate=400kHz

  Gauge=Hygauge.HY4245(i2c_0, address = 0x55)
#   ChipType=Gauge.SubCmdRead(Gauge.ChipType)
#   Version=Gauge.SubCmdRead(Gauge.Version)
#   DesignCapacity=Gauge.StdCmdRead(Gauge.DesignCapacity)
#   print("Chip Number: HY%4x\r\nFirmware version: V0%4x" % (ChipType,Version))
#   print("Design Capacity: %dmAh" % (DesignCapacity))
#   delay(2000)

  while True:
    if TimerDone == True:
      Volt=Gauge.StdCmdRead(Gauge.Voltage)
      Amp=Gauge.StdCmdRead(Gauge.AverageCurrent)
      if (Amp>32767):
        Amp=Amp-65536
      Temp=(Gauge.StdCmdRead(Gauge.Temperature))/10-273.0
    #   FCC=Gauge.StdCmdRead(Gauge.FullChargeCapacity)
    #   RM=Gauge.StdCmdRead(Gauge.RemainingCapacity)
      RSOC=Gauge.StdCmdRead(Gauge.RelativeStateOfCharge)

      print("\r\nVoltage is %dmV.\r\nCurrent is %dmA." % (Volt,Amp))
      print("Temperature is %.1f*C." % (Temp))
    #   print("FullChargeCapacity is %dmAh." % (FCC))
    #   print("RemainingCapacity is %dmAh." % (RM))
      print("RelativeStateOfCharge is %d%%." % (RSOC))
      TimerDone = False

    if KeyDone == True:      #Press A Key
      break

  i2c_0.deinit()