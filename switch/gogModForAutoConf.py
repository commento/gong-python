"""
Support for switching Arduino pins on and off.
So far only digital pins are supported.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.arduino/
"""
import logging
import threading

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import CONF_NAME

#from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
#from homeassistant.components.device_tracker import (
#    PLATFORM_SCHEMA, DOMAIN, ATTR_ATTRIBUTES, ENTITY_ID_FORMAT, DeviceScanner)
#from homeassistant.components.zone import active_zone
#from homeassistant.helpers.event import track_utc_time_change
# import homeassistant.helpers.config_validation as cv
# from homeassistant.util import slugify
# import homeassistant.util.dt as dt_util
# from homeassistant.util.location import distance
# from homeassistant.loader import get_component

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['gatt==0.2.2']

SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
CHARACTERISTIC2 = '6e400003-b5a3-f393-e0a9-e50e24dcca9e' #HEX VALUE of char "x" = 0x78
CHARACTERISTIC = '6e400002-b5a3-f393-e0a9-e50e24dcca9e' #actuator HEX VALUE = 0x00

import gatt

#_CONFIGURING = {}

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()

    def connect_failed(self, error):
        super().connect_failed(error)

    def disconnect_succeeded(self):
        super().disconnect_succeeded()

    def services_resolved(self):
        super().services_resolved()

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

        characteristic2.enable_notifications()
        _LOGGER.error("written value characteristic2")

        characteristic.write_value([120]) 
        _LOGGER.error("written value characteristic")


# def icloud_trusted_device_callback(self, callback_data):
#     """The trusted device is chosen."""

#     _trusted_device = int(callback_data.get('trusted_device'))
#     _LOGGER.error(_trusted_device)

#     return 1

# def icloud_verification_callback(self, callback_data):
#     self._verification_code = callback_data.get('code')
#     _LOGGER.error("written value characteristic")

#     return 1


# self._trusted_device = self.api.trusted_devices[self._trusted_device]

# if not self.api.send_verification_code(self._trusted_device):
#     _LOGGER.error('Failed to send verification code')
#     self._trusted_device = None
#     return

# if self.accountname in _CONFIGURING:
#     request_id = _CONFIGURING.pop(self.accountname)
#     configurator = get_component('configurator')
#     configurator.request_done(request_id)

# # Trigger the next step immediately
# self.icloud_need_verification_code()



#accountname = ""

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Gong platform."""

    switches = []
    switches.append(GongSwitch())
    add_devices(switches)

    ####################################################

    # configurator = get_component('configurator')
    # _CONFIGURING[accountname] = configurator.request_config(
    #     hass, 'Gong {}'.format(accountname),
    #     icloud_trusted_device_callback,
    #     description=(
    #         'Please choose your trusted device by entering'
    #         ' the index from this list: '),
    #     entity_picture="",
    #     submit_caption='Confirm',
    #     fields=[{'id': 'trusted_device', 'name': 'Trusted Device'}]
    # )

    # configurator = get_component('configurator')
    # _CONFIGURING[accountname] = configurator.request_config(
    #         hass, 'iCloud {}'.format(accountname),
    #         icloud_verification_callback,
    #         description=('Please enter the validation code:'),
    #         entity_picture="/static/images/config_icloud.png",
    #         submit_caption='Confirm',
    #         fields=[{'id': 'code', 'name': 'code'}]
    #     )

class GongSwitch(SwitchDevice):
    """Representation of an Gong switch."""

    def __init__(self):
        """Initialize the Pin."""
        self._name = 'Gong'
        self.pin_type = 'digital'
        self.direction = 'out'

        self._state = False #options.get(CONF_INITIAL)

        manager = gatt.DeviceManager(adapter_name='hci0')
        self.device = AnyDevice(mac_address='C7:59:CD:40:8D:CD', manager=manager)
        self.device.connect()

        threading.Thread(target=manager.run).start()

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
        #self._state = True

        self.device.play_gong()

    def turn_off(self):
        """Turn the pin to low/off."""
        _LOGGER.error("TURN OFF")
        self._state = False
