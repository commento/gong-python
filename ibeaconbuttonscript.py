import gatt
import threading
import binascii

from time import sleep, time

SERVICE = '0000aa10-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000aa16-0000-1000-8000-00805f9b34fb' #16 button - 12 motion

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

        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)
        #if self.is_connected() is True:
        print("enable notification characteristic")
        #characteristic.read_value()
        print(characteristic)
        characteristic.enable_notifications()

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("characteristic_enable_notifications_succeeded")
        # device_information_service = next(
        #     s for s in self.services
        #     if s.uuid == SERVICE)
        print(characteristic)
        # characteristic = next(
        #     c for c in device_information_service.characteristics
        #     if c.uuid == CHARACTERISTIC)
        #characteristic.read_value()

    def characteristic_enable_notifications_failed(self, characteristic, error):
        super().characteristic_enable_notifications_failed(characteristic, error)
        print("characteristic_enable_notifications_failed")

    def temperature_read(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)
        #if self.is_connected() is True:
        print("enable notification characteristic")
        characteristic.enable_notifications()
        print("read value from characteristic")

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
    # now = time()
    # if now - prev_update_time >= 5:
    #     print("temperature update")
    #     if(device.is_connected()):
    #         device.temperature_read()
    #     else:
    #         device.connect()
    #         device.temperature_read()
    #     prev_update_time = now
    name = input("x ")
    if name == "x":
        manager.stop()
        break
    if device.is_connected() is not True:
        device.connect()
    sleep(0.05)
