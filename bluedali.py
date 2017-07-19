import gatt
import threading

SERVICE = '0000cbbb-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000cbb1-0000-1000-8000-00805f9b34fb'

manager = gatt.DeviceManager(adapter_name='hci0')

state = None
characteristic = None

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

        global characteristic
        if characteristic is not None:
            characteristic.enable_notifications(enabled=False)

        self.connect()

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)
        global characteristic
        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        characteristic.enable_notifications()

    def play_gong(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        #characteristic.enable_notifications()
        global state
        if state is True:
            characteristic.write_value([1,254,0,0,0,0])
            state = False
        else:
            state = True
            characteristic.write_value([1,254,254,0,0,0])
        print("written value characteristic")

    def characteristic_value_updated(self, characteristic, value):
        print("value", value)

    def play_gung(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)
        characteristic.write_value([0,1,160]) #144



device = AnyDevice(mac_address='00:A0:50:E4:C6:32', manager=manager)
device.connect()
print("device.connect()")

threading.Thread(target=manager.run).start()

while True:
    name = input("x ")
    if name is "x":
        print("do the gong")
        device.play_gong()
    elif name is "y":
        device.play_gung()
    else:
        manager.stop()
        break
