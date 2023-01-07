import utime
'''
AT+MRG , Get Mesh Role 
AT+DIS 0/1 , en/disable discovery mesh node
AT+PBADVCON , enable provisioning channel
AT+PROV , Provision the node
AT+AKA , assign app_key and network_kep to node
AT+MAKB, Set model 
AT+
'''
NonReturnList = ['AT+NL', 'AT+CDG', 'AT+NSO']


class MeshProv:

    def __init__(self, uart):

        self.ble = uart
        self.ROLE = self.WriteCMD_withResp('AT+MRG')[0]
        self.bind_addr = []

    def __del__(self):
        self.ble.deinit()

    def WriteCMD_withResp(self, atcmd, timeout=300):
        self.ble.read(self.ble.any())
        self.ble.write(atcmd+'\r\n')
        utime.sleep_ms(timeout)
        if atcmd in NonReturnList:
            return ('')
        msg = ''
        while 'ERROR' in msg or len(msg) == 0:
            msg = str(self.ble.readline(), 'utf-8').strip()
            utime.sleep_ms(300)
        if 'SUCCESS' in msg:
            msg = msg.split(' ')
            del msg[0:2]
            return (msg)

    def ScanNonProv(self, timeout=5000):

        NonProvDevice = {}
        self.WriteCMD_withResp('AT+DIS 1')
        msg = ''
        prvMills = utime.ticks_ms()
        print('wait 5sec for scan')
        while len(NonProvDevice) < 5 and (utime.ticks_ms()-prvMills) < timeout:
            msg = str(self.ble.readline(), 'utf-8').strip()
            if len(msg) > 0:
                print(msg)
                msg = msg.split(' ')
                NonProvDevice[msg[1]] = msg[3]

            utime.sleep_ms(100)
        self.WriteCMD_withResp('AT+DIS 0')
        return (NonProvDevice)

    def bind_all(self):

        NonProvDevice = self.ScanNonProv()
        if len(NonProvDevice) > 0:
            for key, value in NonProvDevice.items():
                self.WriteCMD_withResp('AT+PBADVCON {}'.format(value))
                id = self.WriteCMD_withResp('AT+PROV')[0]
                self.bind_addr.append(id)
                print('bind-{}'.format(id))
                self.WriteCMD_withResp(
                    'AT+AKA {} 0 0'.format(id,), timeout=500)
                self.WriteCMD_withResp(
                    'AT+MAKB {} 0 0x4005d 0'.format(id,), timeout=500)
                print('bind-OK')

    def DisBind(self, id='00'):
        if id == '00':
            self.WriteCMD_withResp('AT+NR')
        else:
            self.WriteCMD_withResp('AT+NR {}'.format(id))

    def GetDeviceList(self):
        DeviceList = []
        self.WriteCMD_withResp('AT+NL')
        msg = str(self.ble.readline(), 'utf-8').strip()
        while msg != '':
            DeviceList.append(msg.split(' ')[2])
            msg = str(self.ble.readline(), 'utf-8').strip()
        return (DeviceList)

    def SendData_Light(self, dst, C=0, W=0, R=0, G=0, B=0):
        msg = self.WriteCMD_withResp(
            'AT+MDTS {} 0 0 0 0x87010005{:02x}{:02x}{:02x}{:02x}{:02x}'.format(dst, C, W, R, G, B))

    def SendData_Switch(self, dst, on_off):
        msg = self.WriteCMD_withResp(
            'AT+MDTS {} 0 0 0 0x87020001{:02x}'.format(dst, on_off))

    def SetNode_Group(self, dst, group):
        '''需要增加查詢 Group 有無此Node'''
        msg = self.WriteCMD_withResp(
            'AT+MSAA {} 0 0x4005D {}'.format(dst, group), timeout=700)

    def DelNode_Group(self, dst, group):
        '''需要增加查詢 Group 有無此Node'''
        msg = self.WriteCMD_withResp(
            'AT+MSAD {} 0 0x4005D {}'.format(dst, group), timeout=700)

    def SetNodePublish(self, dst, publish_addr):
        pass

    def ReadMeshMsg(self):
        msg = str(self.ble.readline().strip(), 'utf-8')
        return(msg)
