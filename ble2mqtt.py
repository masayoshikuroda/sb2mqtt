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

register = MQTTRegister('mqtt.local', 1883)

def detection_callback(device, advertisement_data):
    logger.debug(f"Detected device: address={device.address}, name={device.name}, rssi={device.rssi}")
    
    for target in targets:
        if target.match(device, advertisement_data):
            info = target.parse(advertisement_data.manufacturer_data)
            if any(info):
                register.regist(device.address, device. name, device.rssi, info)
            break

scanner = BleScanner(60)

while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scanner.start(detection_callback))

