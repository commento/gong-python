"""
Support for switching Arduino pins on and off.
So far only digital pins are supported.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.arduino/
"""
import logging
from requests import get

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import CONF_NAME


_LOGGER = logging.getLogger(__name__)

#import subprocess



#def toggle_light():
    # url = 'http://senic_dali.local/toggle'
    # headers = {#'x-ha-access': 'YOUR_PASSWORD',
    #    'content-type': 'application/json'}

    # response = get(url, headers=headers)
    # _LOGGER.error(response.text)



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Gong platform."""

    switches = []
    switches.append(DaliSwitch())
    add_devices(switches)

class DaliSwitch(SwitchDevice):
    """Representation of an Gong switch."""

    def __init__(self):
        """Initialize the Pin."""
        self._name = 'Dali'
        self.pin_type = 'digital'
        self.direction = 'out'

        self._state = False #options.get(CONF_INITIAL)


    @property
    def name(self):
        """Get the name of the Gong."""
        return self._name

    @property
    def is_on(self):
        """Return true if pin is high/on."""
        return self._state

    def turn_on(self):
        """Turn the pin to high/on."""
        _LOGGER.error("TURN ON")
        self._state = True

        #toggle_light()
        url = 'http://192.168.1.128/toggle'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)
       #  _LOGGER.error(response.text)

        # bash_com = 'curl http://senic_dali.local/toggle'
        # subprocess.Popen(bash_com)
        # output = subprocess.check_output(['bash','-c', bash_com])


    def turn_off(self):
        """Turn the pin to low/off."""
        _LOGGER.error("TURN OFF")

        #toggle_light()
        url = 'http://192.168.1.128/toggle'
        headers = {'x-ha-access': 'raspberry',
       'content-type': 'application/json'}

        response = get(url, headers=headers)

        # bash_com = 'curl http://senic_dali.local/toggle'
        # subprocess.Popen(bash_com)
        # output = subprocess.check_output(['bash','-c', bash_com])
        #_LOGGER.error(response.text)

        self._state = False
