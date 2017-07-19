"""
Support for switching Arduino pins on and off.
So far only digital pins are supported.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.arduino/
"""
import logging
import threading

from homeassistant.const import CONF_NAME
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_RGB_COLOR, SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP, SUPPORT_RGB_COLOR, Light)
from homeassistant.components.light import \
    PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA
from homeassistant.util import color as color_util
from homeassistant.const import CONF_HOSTS

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['gatt==0.2.3']

SERVICE = '0000cbbb-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC = '0000cbb1-0000-1000-8000-00805f9b34fb'

import gatt


class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        _LOGGER.error("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        _LOGGER.error("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        _LOGGER.error("[%s] Disconnected" % (self.mac_address))
        self.connect()

    #is there any feedback when services are resolved
    def services_resolved(self):
        super().services_resolved()

    def turn_on(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        characteristic.write_value([1,254,254,0,0,0])

    def turn_off(self):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE)

        characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == CHARACTERISTIC)

        characteristic.write_value([1,254,0,0,0,0])

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Arduino platform."""

    lights = []
    lights.append(BlueDaliLight())
    add_devices(lights)

class BlueDaliLight(Light):
    """Representation of an Arduino switch."""

    def __init__(self):
        """Initialize the Pin."""
        self._name = 'BlueDali' 
        self.pin_type = 'digital'
        self.direction = 'out'

        self._state = 'false'

        self._first = 1

        manager = gatt.DeviceManager(adapter_name='hci0')
        self.device = AnyDevice(mac_address='00:A0:50:E4:C6:32', manager=manager)
        self.device.connect()
        _LOGGER.error("device.connect()")

        threading.Thread(target=manager.run).start()

    @property
    def name(self):
        """Get the name of the pin."""
        return self._name

    @property
    def is_on(self):
        """Return true if pin is high/on."""
        return self._state

    def turn_on(self):
        """Turn the pin to high/on."""
        self._state = True
        _LOGGER.error("TURN ON")
        self.device.turn_on()

    def turn_off(self):
        """Turn the pin to low/off."""
        _LOGGER.error("TURN OFF")
        self.device.turn_off()
        self._state = False
