

def setup(hass, config):
    """Set up the connection to the KNX IP interface."""

def close_tunnel(_data):
    """Close the NKX tunnel connection on shutdown."""

class KNXConfig(object):
    """Handle the fetching of configuration from the config file."""

    def __init__(self, config):
        """Initialize the configuration."""
        from knxip.core import parse_group_address #interesting

        self.config = config
        self.should_poll = config.get('poll', True)
        if config.get('address'):
            self._address = parse_group_address(config.get('address'))
        else:
            self._address = None
        if self.config.get('state_address'):
            self._state_address = parse_group_address(
                self.config.get('state_address'))
        else:
            self._state_address = None

    @property
    def address(self):
        """Return the address of the device as an integer value.

        3 types of addresses are supported:
        integer - 0-65535
        2 level - a/b
        3 level - a/b/c
        """
        return self._address

    @property
    def state_address(self):
        """Return the group address the device sends its current state to.

        Some KNX devices can send the current state to a seperate
        group address. This makes send e.g. when an actuator can
        be switched but also have a timer functionality.
        """
        return self._state_address


class KNXGroupAddress(Entity):
    """Representation of devices connected to a KNX group address."""

    def __init__(self, hass, config):
        """Initialize the device."""
        self._config = config
        self._state = False
        self._data = None
        _LOGGER.debug("Initalizing KNX group address %s", self.address)

        def handle_knx_message(addr, data):
            """Handle an incoming KNX frame.

            Handle an incoming frame and update our status if it contains
            information relating to this device.
            """
            if (addr == self.state_address) or (addr == self.address):
                self._state = data[0]
                self.schedule_update_ha_state()

        KNXTUNNEL.register_listener(self.address, handle_knx_message)
        if self.state_address:
            KNXTUNNEL.register_listener(self.state_address, handle_knx_message)

    @property
    def name(self):
        """Return the entity's display name."""
        return self._config.name

    @property
    def config(self):
        """Return the entity's configuration."""
        return self._config

    @property
    def should_poll(self):
        """Return the state of the polling, if needed."""
        return self._config.should_poll

    @property
    def is_on(self):
        """Return True if the value is not 0 is on, else False."""
        return self._state != 0

    @property
    def address(self):
        """Return the KNX group address."""
        return self._config.address

    @property
    def state_address(self):
        """Return the KNX group address."""
        return self._config.state_address

    @property
    def cache(self):
        """Return the name given to the entity."""
        return self._config.config.get('cache', True)

    def group_write(self, value):
        """Write to the group address."""
        KNXTUNNEL.group_write(self.address, [value])

    def update(self):
        """Get the state from KNX bus or cache."""
        from knxip.core import KNXException

        try:
            if self.state_address:
                res = KNXTUNNEL.group_read(
                    self.state_address, use_cache=self.cache)
            else:
                res = KNXTUNNEL.group_read(self.address, use_cache=self.cache)

            if res:
                self._state = res[0]
                self._data = res
            else:
                _LOGGER.debug(
                    "Unable to read from KNX address: %s (None)", self.address)

        except KNXException:
            _LOGGER.exception(
                "Unable to read from KNX address: %s", self.address)
            return False




# only termostat is implemented with this element (but is not the same setup we have for the actuator?)
class KNXMultiAddressDevice(Entity):
    """Representation of devices connected to a multiple KNX group address.

    This is needed for devices like dimmers or shutter actuators as they have
    to be controlled by multiple group addresses.
    """
