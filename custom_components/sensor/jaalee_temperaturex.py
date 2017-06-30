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
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, TEMP_CELSIUS, STATE_UNKNOWN, EVENT_HOMEASSISTANT_STOP,
    EVENT_HOMEASSISTANT_START)

REQUIREMENTS = ['gatt==0.2.3']

SERVICE = '0000ffb0-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000ffb1-0000-1000-8000-00805f9b34fb'

SERPASS = '0000fff0-0000-1000-8000-00805f9b34fb'
CHARPASS = '0000fff1-0000-1000-8000-00805f9b34fb'

manager = gatt.DeviceManager(adapter_name='hci0')

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
        characteristic.enable_notifications(enabled=False)
        self.connect()

    def services_resolved(self):
        super().services_resolved()
        # insert password

        global characteristic
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERPASS)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARPASS)

        characteristic.write_value([102, 102, 102])


    #def read_temperature(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        characteristic.enable_notifications()

        #_LOGGER.info(characteristic.read_value())
        _LOGGER.info("read value characteristic")

    def characteristic_value_updated(self, characteristic, value):
        hexvalue = binascii.hexlify(value)
        intvalue = int(hexvalue, 16)
        _LOGGER.info(intvalue)
        if intvalue != 0:
            temperature = -46.86 + 175.72 * (intvalue/65536)
            self.jaalee_entity.temperature = '%.2f'%(temperature)
        else:
            self.jaalee_entity.temperature = STATE_UNKNOWN
        _LOGGER.info(self.jaalee_entity.temperature)
        self.jaalee_entity.schedule_update_ha_state()

    def characteristic_read_value_failed(self, characteristic, error):
        _LOGGER.info("characteristic_read_value_failed, set temperature to STATE_UNKNOWN")
        self.jaalee_entity.temperature = STATE_UNKNOWN


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Validate configuration, create devices and start monitoring thread."""

    devices = []
    # TODO: configure more device with the same component
    global entities
    entity = JaaleeEntity('FF:F3:F0:A2:1A:35')
    devices.append(entity)

    if devices:
        add_devices(devices)
    else:
        _LOGGER.warning("No devices were added")
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, close_tunnel)

def close_tunnel(_data):
    """Close the NKX tunnel connection on shutdown."""
    _LOGGER.warning("manager stop")
    manager.stop()

class JaaleeEntity(Entity):
    """Representation of a temperature sensor."""

    def __init__(self, mac_address):
        """Initialize a sensor."""
        self._name = "iBeaconTemperature"
        self.temperature = STATE_UNKNOWN

        # TODO: add a configurable mac address
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
    def state(self):
        """Return the state of the device."""
        return self.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return TEMP_CELSIUS

    def update(self):
        """Get the latest value from the pin."""
        #if self.device.is_connected():
        _LOGGER.info("is connected?")
            #self.device.read_temperature()
        #else:
        #    self.device.connect()
        #    _LOGGER.info("is not connected, reconnect")
            #self.device.read_temperature()
        _LOGGER.info(self.device)
