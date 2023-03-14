from machine import UART, LED, Switch
from utime import sleep, ticks_ms, ticks_diff
import gc
import ubinascii as binascii

from MESHDevice import MeshDevice as Mesh_D

Req_CMD = [0x01, 0x03, 0x00, 0x00, 0x00, 0x09, 0x85, 0xCC]
air_Sensor_port = UART(0, 9600, timeout=350, read_buf_len=256)

try:
    uart = UART(1, 115200, timeout=20)
except:
    uart.deinit()
    uart = UART(1, 115200, timeout=20)
uart.read(uart.any())


def chek_node_reset_key():
    pre_ticks_ms = ticks_ms()
    while key.value():
        if ticks_diff(ticks_ms(), pre_ticks_ms) > 1000:
            MD.NodeReset()
            # print('reset_node')
            while True:
                type1, data1 = MD.uart_recv()
                if type1 == 'SYS-MSG' and ('DEVICE' in data1):
                    break
            break


def read_air():
    air_Sensor_port.read(air_Sensor_port.any())  # Clear UART RX Buffer
    air_Sensor_port.write(bytearray(Req_CMD))
    sleep(0.1)
    data = air_Sensor_port.readline()
    if len(data) == 23:
        if data[0] == 0x01 and data[1] == 0x03 and data[2] == 0x12:
            header = bytes([0x87, 0xF0, 0x00])
            mac_addr = binascii.unhexlify(MD.mac_addr[7:-1])
            dst_addr = bytes([0xFF, 0xFE])  # to Provisioner
            data_length = bytes([0x0A])
            op_code = bytes([0x06, 0x00])
            PM2_5 = bytes(data[3:5])
            TEMPER = bytes(data[5:7])
            HUMIT = bytes(data[7:9])
            CO2 = bytes(data[9:11])
            MD.Send_mesh_data(header+mac_addr+dst_addr +
                              data_length+op_code + PM2_5 + TEMPER+HUMIT+CO2)
            run_index.toggle()


prov_index = LED('ledr')
run_index = LED('ledy')
key = Switch('keya')
prov_index.on()
run_index.on()
sleep(1)
prov_index.off()
run_index.off()

uart.write('AT+VER\r\n')
sleep(0.1)
_ = uart.read(uart.any())

MD = Mesh_D(uart)
while True:
    gc.collect()
    type1, data1 = MD.uart_recv()
    if MD.prov_state != 'PROV-ED':
        prov_index.toggle()
        sleep(0.5)
    else:
        chek_node_reset_key()
        read_air()
        sleep(0.5)
