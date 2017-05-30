"""
Read temperature information from Eddystone beacons.

Your beacons must be configured to transmit UID (for identification) and TLM
(for temperature) frames.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.eddystone_temperature/
"""
import logging
import gatt
import threading
import binascii

import voluptuous as vol
from time import sleep, time

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, TEMP_CELSIUS, STATE_UNKNOWN, EVENT_HOMEASSISTANT_STOP,
    EVENT_HOMEASSISTANT_START)

REQUIREMENTS = ['gatt==0.2.2']

SERVICE = '0000ffb0-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000ffb1-0000-1000-8000-00805f9b34fb'

manager = gatt.DeviceManager(adapter_name='hci0')

_LOGGER = logging.getLogger(__name__)

temp = 0

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        _LOGGER.info("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        _LOGGER.info("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        _LOGGER.info("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        _LOGGER.info("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            _LOGGER.info("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                _LOGGER.info("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

    def temperature_read(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        _LOGGER.info(characteristic.read_value())
        _LOGGER.info("read value characteristic")

    def characteristic_value_updated(self, characteristic, value):
        #_LOGGER.info(value)
        hexvalue = binascii.hexlify(value)
        intvalue = int(hexvalue, 16)
        _LOGGER.info(intvalue)
        temp = -46.86 + 175.72 * (intvalue/65536)
        _LOGGER.info(temp)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Validate configuration, create devices and start monitoring thread."""
    #bt_device_id = "Temperature" #config.get("bt_device_id")

    #beacons = config.get("beacons")
    devices = []

    devices.append(EddystoneTemp())

    if devices:
        mon = Monitor(hass, devices)

        def monitor_stop(_service_or_event):
            """Stop the monitor thread."""
            _LOGGER.info("Stopping scanner for Eddystone beacons")
            mon.stop()

        def monitor_start(_service_or_event):
            """Start the monitor thread."""
            _LOGGER.info("Starting scanner for Eddystone beacons")
            mon.start()

        add_devices(devices)
        mon.start()
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, monitor_stop)
        hass.bus.listen_once(EVENT_HOMEASSISTANT_START, monitor_start)
    else:
        _LOGGER.warning("No devices were added")


class EddystoneTemp(Entity):
    """Representation of a temperature sensor."""

    def __init__(self):
        """Initialize a sensor."""
        self._name = "CIAO"
        self.temperature = STATE_UNKNOWN

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return TEMP_CELSIUS

    @property
    def should_poll(self):
        """Return the polling state."""
        return False


class Monitor(object):
    """Continously scan for BLE advertisements."""

    def __init__(self, hass, devices):
        """Construct interface object."""
        self.hass = hass

        # List of beacons to monitor
        self.devices = devices
        # Number of the bt device (hciX)
        #self.bt_device_id = 0

        # def callback(bt_addr, _, packet, additional_info):
        #     """Handle new packets."""
        #     self.process_packet()

        # pylint: disable=import-error
        # from beacontools import (
        #     BeaconScanner, EddystoneFilter, EddystoneTLMFrame)
        # device_filters = [EddystoneFilter(d.namespace, d.instance)
        #                   for d in devices]

        # self.scanner = BeaconScanner(
        #     callback, 0)
        # self.scanning = False

    def start(self):

        device = AnyDevice(mac_address='FF:F3:F0:A2:1A:35', manager=manager)
        device.connect()
        _LOGGER.info("device.connect()")

        t1 = threading.Thread(target=manager.run)
        t1.start()
        prev_update_time = time()

        while True:
            now = time()
            if now - prev_update_time >= 60:
                _LOGGER.info("temperature update")
                if(device.is_connected()):
                    device.temperature_read()
                else:
                    device.connect()
                    device.temperature_read()
                for dev in self.devices:
                    _LOGGER.info(dev)
                    _LOGGER.info(temp)
                    _LOGGER.info(dev.temperature)
                    if temp != dev.temperature:
                        dev.temperature = temp
                    #     dev.schedule_update_ha_state()
                prev_update_time = now

            sleep(0.05)
        """Continously scan for BLE advertisements."""
        # if not self.scanning:
        #     self.scanner.start()
        #     self.scanning = True
        # else:
        #     _LOGGER.debug(
        #         "start() called, but scanner is already running")



    # def process_packet(self, namespace, instance, temperature):
    #     """Assign temperature to device."""
    #     _LOGGER.debug("Received temperature for <%s,%s>: %d",
    #                   namespace, instance, temperature)

    #     for dev in self.devices:
    #         if dev.namespace == namespace and dev.instance == instance:
    #             if dev.temperature != temperature:
    #                 dev.temperature = temperature
    #                 dev.schedule_update_ha_state()

    def stop(self):
        _LOGGER.info("manager.stop()")
        manager.stop()

        """Signal runner to stop and join thread."""
        # if self.scanning:
        #     _LOGGER.debug("Stopping...")
        #     self.scanner.stop()
        #     _LOGGER.debug("Stopped")
        #     self.scanning = False
        # else:
        #     _LOGGER.debug(
        #         "stop() called but scanner was not running")
