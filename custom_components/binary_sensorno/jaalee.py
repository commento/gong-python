"""
Read temperature information from Jaalee beacons.

Your beacons must be configured to transmit temperature with the eBeacon app.

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
from homeassistant.components.binary_sensor import (
    BinarySensorDevice, DEVICE_CLASSES_SCHEMA, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME, TEMP_CELSIUS, STATE_UNKNOWN, EVENT_HOMEASSISTANT_STOP,
    EVENT_HOMEASSISTANT_START)

REQUIREMENTS = ['gatt==0.2.3']

SERVICE = '0000aa10-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000aa16-0000-1000-8000-00805f9b34fb'

SERPASS = '0000fff0-0000-1000-8000-00805f9b34fb'
CHARPASS = '0000fff1-0000-1000-8000-00805f9b34fb'

manager = gatt.DeviceManager(adapter_name='hci1')

_LOGGER = logging.getLogger(__name__)

entities = []

characteristic = None

class JaaleeDevice(gatt.Device):

    def __init__(self, mac_address, jaalee_entity):
        global manager
        super().__init__(mac_address, manager)
        self.jaalee_entity = jaalee_entity

    def connect_succeeded(self):
        super().connect_succeeded()
        _LOGGER.info("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        _LOGGER.info("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        _LOGGER.info("[%s] Disconnected" % (self.mac_address))
        global characteristic
        print(characteristic)
        characteristic.enable_notifications(enabled=False)
        #sleep(2)
        self.connect()

    def services_resolved(self):
        super().services_resolved()

        # insert password
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERPASS)

        global characteristic
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

        _LOGGER.info("enable notification characteristic")

        _LOGGER.info(characteristic)
        characteristic.enable_notifications()

    def characteristic_value_updated(self, characteristic, value):
        _LOGGER.info(value)
        hexvalue = binascii.hexlify(value)
        _LOGGER.info(hexvalue)

        if hexvalue == 0x01:
            _LOGGER.info("click")

        elif hexvalue == 0x03:
            _LOGGER.info("long click")

        self.jaalee_entity._state = not self.jaalee_entity._state
        _LOGGER.info(self.jaalee_entity._state)
        self.jaalee_entity.schedule_update_ha_state()

    def characteristic_read_value_failed(self, characteristic, error):
        _LOGGER.info("characteristic_read_value_failed, set temperature to STATE_UNKNOWN")

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("characteristic_enable_notifications_succeeded")

    def characteristic_enable_notifications_failed(self, characteristic, error):
        super().characteristic_enable_notifications_failed(characteristic, error)
        print("characteristic_enable_notifications_failed")

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Validate configuration, create devices and start monitoring thread."""

    devices = []
    # TODO: configure more device with the same component
    global entities
    entity = JaaleeBinarySensor('DC:C1:2E:9D:30:90')
    devices.append(entity)

    if devices:
        add_devices(devices)
    else:
        _LOGGER.warning("No devices were added")

class JaaleeBinarySensor(BinarySensorDevice):
    """Representation of a temperature sensor."""

    def __init__(self, mac_address):
        """Initialize a sensor."""
        self._name = "iBeaconBinary"
        self._state = False

        # TODO: add a configurable mac address
        #self.device = JaaleeDevice(mac_address, self)

        #self.device.connect()
        _LOGGER.info("device.connect()")

        t1 = threading.Thread(target=manager.run)
        t1.start()
        self.device = JaaleeDevice(mac_address, self)

        self.device.connect()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    def update(self):
        """Get the latest value from the pin."""
        if self.device.is_connected():
            _LOGGER.info("is connected")
        else:
            _LOGGER.info("self.device.disconnect()")
            self.device.connect()
            _LOGGER.info("is not connected, reconnect")
