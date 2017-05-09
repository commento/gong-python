"""
Support for switching Arduino pins on and off.
So far only digital pins are supported.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.arduino/
"""
import logging
from requests import get
import json

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import CONF_NAME
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_RGB_COLOR, SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP, SUPPORT_RGB_COLOR, Light)
from homeassistant.components.light import \
    PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA
from homeassistant.util import color as color_util

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Gong platform."""

    lights = []
    lights.append(DaliLight())
    add_devices(lights)

class DaliLight(Light):
    """Representation of an Gong switch."""

    def __init__(self):
        """Initialize the Pin."""
        self._name = 'Dali'
        self.pin_type = 'digital'
        self.direction = 'out'

        self._state = False #options.get(CONF_INITIAL)

        url = 'http://192.168.1.128'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)

        json_data = json.loads(response.text)

        state = json_data['state']

        if state == 'on':
            self._state = True
        else:
            self._state = False

    @property
    def supported_features(self):
        """Flag supported features."""
        return 1 #self._features

    @property
    def name(self):
        """Get the name of the Dali."""
        return self._name

    @property
    def is_on(self):
        """Return true if pin is high/on."""

        return self._state

    @property
    def brightness(self):
        """Brightness of the light (an integer in the range 1-255)."""
        return 1 #self._light_data.dimmer

    @property
    def color_temp(self):
        """Return the CT color value in mireds."""
        # if (self._light_data.hex_color is None or
        #         self.supported_features & SUPPORT_COLOR_TEMP == 0 or
        #         not self._ok_temps):
        #     return None

        # kelvin = next((
        #     kelvin for kelvin, hex_color in self._ok_temps.items()
        #     if hex_color == self._light_data.hex_color), None)
        # if kelvin is None:
        #     _LOGGER.error(
        #         'unexpected color temperature found for %s: %s',
        #         self.name, self._light_data.hex_color)
        #     return
        return 1 #color_util.color_temperature_kelvin_to_mired(kelvin)

    @property
    def rgb_color(self):
        """RGB color of the light."""
        return None

    def turn_on(self):
        """Turn the pin to high/on."""
        _LOGGER.error("DALI TURN ON")

        url = 'http://192.168.1.128/toggle'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)
        _LOGGER.error(response.text)

        json_data = json.loads(response.text)
        _LOGGER.error(json_data)

        state = json_data['state']

        if state == 'on':
            self._state = True
        else:
            self._state = False
            _LOGGER.error("DALI light unexpected state")


    def turn_off(self):
        """Turn the pin to low/off."""
        _LOGGER.error("DALI TURN OFF")
        self._state = False


        url = 'http://192.168.1.128/toggle'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)
        _LOGGER.error(response.text)

        json_data = json.loads(response.text)
        _LOGGER.error(json_data)

        state = json_data['state']

        if state == 'on':
            self._state = True
            _LOGGER.error("DALI light unexpected state")
        else:
            self._state = False


