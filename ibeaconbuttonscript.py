import gatt
import threading
import binascii

from time import sleep, time

SERVICE = '0000aa10-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000aa16-0000-1000-8000-00805f9b34fb' #16 button - 12 motion

SERPASS = '0000fff0-0000-1000-8000-00805f9b34fb'
CHARPASS = '0000fff1-0000-1000-8000-00805f9b34fb'

PASSWORD = 0x666666


manager = gatt.DeviceManager(adapter_name='hci0')


class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        # self.connect()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        # self.connect()

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

        device_information_service = next(
            s for s in self.services
            if s.uuid == SERPASS)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARPASS)

        characteristic.write_value([102, 102, 102])

        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        print("enable notification characteristic")
        characteristic.enable_notifications()

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("characteristic_enable_notifications_succeeded")

    def characteristic_enable_notifications_failed(self, characteristic, error):
        super().characteristic_enable_notifications_failed(characteristic, error)
        print("characteristic_enable_notifications_failed")

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_enable_notifications_failed(characteristic, value)
        print("characteristic_value_updated")
        print(value)


device = AnyDevice(mac_address='DC:C1:2E:9D:30:90', manager=manager)
device.connect()
print("device.connect()")

t1 = threading.Thread(target=manager.run)
t1.start()
prev_update_time = time()

while True:
    name = input("x ")
    if name == "x":
        manager.stop()
        break
    sleep(0.05)
