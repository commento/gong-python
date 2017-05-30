import gatt
import threading
import binascii

SERVICE = '0000ffb0-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000ffb1-0000-1000-8000-00805f9b34fb' #temperature

manager = gatt.DeviceManager(adapter_name='hci0')



class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

    def play_gong(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        print(characteristic.read_value()) 
        print("read value characteristic")

    def characteristic_value_updated(self, characteristic, value):
        print(value)
        hexvalue = binascii.hexlify(value)
        intvalue = int(hexvalue, 16)
        print(intvalue)
        temp = -46.86 + 175.72 * (intvalue/65536)
        print(temp)
#        dec = value.decode('utf-8', 'backslashreplace')
#        print("temperature: ", dec)
#        print(ord(dec))

device = AnyDevice(mac_address='FF:F3:F0:A2:1A:35', manager=manager)
device.connect()
print("device.connect()")

t1 = threading.Thread(target=manager.run)
t1.start()

while True:
    name = input("x ")
    if name == "x":
        print("do the gong")
        if(device.is_connected()):
            device.play_gong()
        else:
            device.connect()
            device.play_gong()
    else:
        manager.stop()
        break
