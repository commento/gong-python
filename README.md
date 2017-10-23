# gong-python
this is a repository initially created to versioning a python script used to play an arduino-actuated-Gong with Home Assistant.
Then, it became a backup for all the scripts and Home Assistant integrations I worked on:

- [enOcean](#enocean)
- [KNX](#knx)
- [Dali over Wifi](#dali-over-wifi)
- [Dali over BLE](#dali-over-ble)
- [Jaalee iBeacon button](#jaalee-ibeacon-button)
- [Jaalee iBeacon temperature sensor](#jaalee-ibeacon-temperature-sensor)
- [nmap based location tracking](#nmap-based-location-tracking)
- [IFTTT](#ifttt)
- [Slack integration](#slack-integration)
- [Osram Ligthify](#osram-ligthify)
- [Lifx](#lifx)
- [Philips Hue](#philips-hue)
- [Sonos](#sonos)
- [Bose](#bose)
- [Gong](#gong)
- [Home Assistant Automation](#home-assistant-automation)

The main configuration is stored in `configuration.yaml`.
In the main folder all the scripts developed to test the device fuctionality are present.
The sub-folders contain Home Assistant integrations.

Home-Assistant-related known issues are collected under https://github.com/getsenic/senic-hub/issues with the tag HA. 

## Device specific information
Here collected some useful information that can be used to setup the HA components

### enOcean
enOcean binary sensor integration works configuring Home Assistant as visible in the configuration file.
```
enocean:
  device: /dev/tty????

binary_sensor:
  - platform: enocean
    name: "button sensor"
    id: [0x??,0x??,0x??,0x??]
```
The id is an hardware identifier reported on the back of the device.
As specified in the Home Assistant documentation: https://home-assistant.io/components/enocean/
only some enOcean devices are confirmed to work.

### KNX
KNX scan does not work as expected. So the host ip address has to be added manually in the configuration file:
```
knx:
  host: ??.??.??.??
```
All the other specific devices in the system has to be configured using their assigned KNX group addresses as explained at:
https://home-assistant.io/components/knx/

### Dali over Wifi
The Dali over Wifi implementation is based on the demo device implemented in the private repository: https://github.com/getsenic/esp8266-dali
The Home Assistant component is located in the folder light, file dali.py:
https://github.com/commento/gong-python/blob/master/light/dali.py

As for all the custom components, the implementation has to be placed according to these instructions:
https://home-assistant.io/developers/creating_components/

### Dali over BLE
The Dali over BLE implementation is basically an Home Assistant integration of the iLumTech Bluebridge device.
The Home Assistant component is located in the folder light, file bluedali.py:
https://github.com/commento/gong-python/blob/master/light/bluedali.py

### Jaalee iBeacon button
The custom component implementation for the Jaalee iBeacon button is located in custom_components/binary_sensor:
https://github.com/commento/gong-python/blob/master/custom_components/binary_sensor/jaalee.py

### Jaalee iBeacon temperature sensor
The custom component implementation for the Jaalee iBeacon button is located in custom_components/sensor:
https://github.com/commento/gong-python/blob/master/custom_components/sensor/jaalee_temperature.py

### nmap based location tracking
Requirements: nmap has to be installed on the OS

### IFTTT

### Slack integration

### Osram Ligthify

### Lifx

### Philips Hue

### Sonos

### Bose

### Gong

### Home Assistant Automation
