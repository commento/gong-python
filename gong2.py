from homeassistant.helpers.entity import ToggleEntity


class Gong(ToggleEntity):
    def __init__(self,path):
        self.path = path

    @property
    def name(self):
    	