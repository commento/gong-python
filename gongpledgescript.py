import gatt
import threading

from lxml import html
import requests

from time import sleep

SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
CHARACTERISTIC2 = '6e400003-b5a3-f393-e0a9-e50e24dcca9e' #HEX VALUE of char "x" = 0x78 number 120
CHARACTERISTIC = '6e400002-b5a3-f393-e0a9-e50e24dcca9e' #actuator HEX VALUE = 0x00

manager = gatt.DeviceManager(adapter_name='hci0')

oldpledge = 0

def check_pledge():
    page = requests.get('https://www.kickstarter.com/projects/802159142/covi-speech-enabled-light-and-open-source-smart-ho')
    tree = html.fromstring(page.content)
    pledge = tree.xpath('//span[@class="block green-700 js-pledged medium type-16 type-24-md"]/text()')
    print(pledge)
#    pledge = pledge[0].replace("$", "")
#    pledge = pledge.replace("€", "")
#    pledge = pledge.replace(",", "")
#    pledge = pledge.replace(".", "")
    print(pledge)
    global oldpledge
    if oldpledge != pledge: # int(pledge) and oldpledge != 0:
        print("play gong")
        device.play_gong()
    oldpledge = pledge

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
#        import traceback; traceback.print_exc()
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

        characteristic2 = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC2)

        characteristic2.enable_notifications() #0x00
        print("written value characteristic2")

        characteristic.write_value([120]) 
        print("written value characteristic")


device = AnyDevice(mac_address='C7:59:CD:40:8D:CD', manager=manager)
device.connect()
print("device.connect()")

t1 = threading.Thread(target=manager.run)
t1.start()

check_pledge()


while True:
    sleep(0.2)
    check_pledge()
#    sleep(0.2)
#    name = input("x ")
#    if name == "x":
#        print("do the gong")
#        print(threading.enumerate())
    if(device.is_connected() is not True):
        device.connect()
#    sleep(0.2)
#        check_pledge()
        #device.play_gong()
#    else:
#        manager.stop()
#        break
