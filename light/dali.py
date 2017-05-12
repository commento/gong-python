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

urlx = 'http://192.168.1.22'

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

        # self._light = light

        # # Caching of LightControl and light object
        # self._light_control = light.light_control
        # self._light_data = light.light_control.lights[0]


        # TODO: change to on
        self._state = False #options.get(CONF_INITIAL)

        url = urlx
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)

        json_data = json.loads(response.text)

        state = json_data['state']

        url = urlx + '/dimstate'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)

        json_data = json.loads(response.text)

        self._dimmer = int(int(json_data['dimState'])*1.5)

        _LOGGER.error(self._dimmer)

        self._state = state == 'on'

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

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
        _LOGGER.error("inside brightness")
        url = urlx + '/dimstate'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)
        _LOGGER.error(response.text)

        json_data = json.loads(response.text)
        _LOGGER.error(json_data)

        state = int(int(json_data['dimState'])*1.5)

        # if int(self._dimmer) < 170:
        self._dimmer = state

        return self._dimmer

    @property
    def rgb_color(self):
        """RGB color of the light."""
        return None

    def turn_on(self, **kwargs):
        """Turn the pin to high/on."""
        _LOGGER.error("DALI TURN ON")

        self._state = True

        if ATTR_BRIGHTNESS in kwargs:
            _LOGGER.error(kwargs[ATTR_BRIGHTNESS])

            bri = kwargs[ATTR_BRIGHTNESS]

            if bri == 0:
                self._state = False
            else:
                bri = int(bri / 1.5)
                _LOGGER.error(bri)


            url = urlx + '/dimset?bri=' + str(bri)
            headers = {'x-ha-access': 'raspberry',
                'content-type': 'application/json'}

            response = get(url, headers=headers)
            _LOGGER.error(response.text)

            json_data = json.loads(response.text)
            _LOGGER.error(json_data)   

            self._dimmer = kwargs[ATTR_BRIGHTNESS]

        else:
            url = urlx + '/toggle'
            headers = {'x-ha-access': 'raspberry',
                'content-type': 'application/json'}

            response = get(url, headers=headers)
            _LOGGER.error(response.text)

            json_data = json.loads(response.text)
            _LOGGER.error(json_data)

            state = json_data['state']
            self._dimmer = 255
            self._state = state == 'on'

    def turn_off(self, **kwargs):
        """Turn the pin to low/off."""
        _LOGGER.error("DALI TURN OFF")
        self._state = False

        url = urlx + '/toggle'
        headers = {'x-ha-access': 'raspberry',
            'content-type': 'application/json'}

        response = get(url, headers=headers)
        _LOGGER.error(response.text)

        json_data = json.loads(response.text)
        _LOGGER.error(json_data)

        state = json_data['state']

        self._dimmer = 0

        self._state = state == 'on'


