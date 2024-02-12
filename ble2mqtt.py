import os
import sys
import logging
import asyncio
from mqtt_register import MQTTRegister
from ble_scanner import BleScanner
from switchbot_device import PlugSwitchBotDevice, MeterSwitchBotDevice

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

targets = []
targets.append(PlugSwitchBotDevice())
targets.append(MeterSwitchBotDevice())

HOST = os.environ.get('MQTT_HOST', 'mqtt.local')
PORT = int(os.environ.get('MQTT_PORT', '1883'))
register = MQTTRegister(HOST, PORT)

def detection_callback(device, advertisement_data):
    logger.debug(f"Detected device: address={device.address}, name={device.name}, rssi={device.rssi}")
    
    for target in targets:
        if target.match(device, advertisement_data):
            info = target.parse(advertisement_data.manufacturer_data)
            if any(info):
                register.regist(device.address, device. name, device.rssi, info)
            break

SCAN_TIME = int(os.environ.get('SCAN_TIME', '60'))
scanner = BleScanner(SCAN_TIME)

while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scanner.start(detection_callback))

