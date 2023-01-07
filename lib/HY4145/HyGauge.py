
from micropython import const
from machine import I2C, Pin

class Hygauge:
  def __init__(self, i2c_bus, address = 0x55):
    self.address = address
    self.i2c_bus = i2c_bus

  def StdCmdRead(self, cmd):  # Gauge Standard Commands Read
    buff=bytearray(2)
    self.i2c_bus.send(cmd,self.address)
    self.i2c_bus.recv(buff,self.address)	# Read 2Byte
    retval = (int(buff[1]) << 8) | buff[0]
    return retval

  def SubCmdRead(self, cmd):  # Gauge Control Subcommands Read
    buff=bytearray(2)
    self.i2c_bus.send(bytearray([0x00,cmd&0xFF,(cmd>>8)&0xFF]),self.address)
    self.i2c_bus.recv(buff,self.address)	# Read 2Byte
    retval = (int(buff[1]) << 8) | buff[0]
    return retval

class HY4145(Hygauge):
  addrHY4145 = const(0x55)   # HY4145 Device ID address for slave target

  # Standard Commands
  Control                   = const(0x00)
  Temperature               = const(0x06)
  Voltage                   = const(0x08)
  Flags                     = const(0x0A)
  AverageCurrent            = const(0x14)
  InternalTemperature       = const(0x28)
  CycleCount                = const(0x2A)
  RelativeStateOfCharge     = const(0x2C)  # RSOC
  StateOfHealth             = const(0x2E)  # SOH
  Current                   = const(0x30)
  SafetyStatus              = const(0x32)
  PassedCharge              = const(0x34)

class HY4245(Hygauge):
  addrHY4245 = const(0x55)   # HY4245 Device ID address for slave target

  # Standard Commands
  Control                   = const(0x00)
  Temperature               = const(0x06)
  Voltage                   = const(0x08)
  Flags                     = const(0x0A)
  Current                   = const(0x0C)
  AverageCurrent            = const(0x14)
  InternalTemperature       = const(0x28)
  CycleCount                = const(0x2A)
  RelativeStateOfCharge     = const(0x2C)  # RSOC
  StateOfHealth             = const(0x2E)  # SOH
