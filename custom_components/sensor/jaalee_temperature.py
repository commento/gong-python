"""
Read temperature information from Jaalee beacons.

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

temp = STATE_UNKNOWN

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
        if intvalue != 0:
            global temp
            temp = -46.86 + 175.72 * (intvalue/65536)
            temp = '%.3f'%(temp)
            _LOGGER.info(temp)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Validate configuration, create devices and start monitoring thread."""

    devices = []

    devices.append(JaaleeTemp())

    if devices:
        add_devices(devices)
    else:
        _LOGGER.warning("No devices were added")


class JaaleeTemp(Entity):
    """Representation of a temperature sensor."""

    def __init__(self):
        """Initialize a sensor."""
        self._name = "iBeaconTemperature"
        self.temperature = STATE_UNKNOWN

        self.device = AnyDevice(mac_address='FF:F3:F0:A2:1A:35', manager=manager)

        self.device.connect()
        _LOGGER.info("device.connect()")

        t1 = threading.Thread(target=manager.run)
        t1.start()

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

    def update(self):
        """Get the latest value from the pin."""
        if(self.device.is_connected()):
            _LOGGER.info("is connected")
            self.device.temperature_read()
        else:
            self.device.connect()
            _LOGGER.info("is not connected, reconnect")
            self.device.temperature_read()
        #for dev in self.devices:
        _LOGGER.info(self.device)

        global temp
        _LOGGER.info(temp)
        _LOGGER.info(self.temperature)
        if self.temperature != temp:
            self.temperature = temp

