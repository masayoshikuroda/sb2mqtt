import os
import sys
import logging
import asyncio
from mqtt_publisher import MQTTPublisher
from ble_scanner import BleScanner
from switchbot_device import PlugSwitchBotDevice, MeterSwitchBotDevice, BotSwitchBotDevice, ContactSwitchBotDevice, Hub2SwitchBotDevice, RemoteSwitchBotDevice, MeterProCO2SwitchBotDevice

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

HOST = os.environ.get('MQTT_HOST', 'localhost')
PORT = int(os.environ.get('MQTT_PORT', '1883'))
TOPIC = os.environ.get('MQTT_TOPIC', 'sb2mqtt')
SCAN_TIME = int(os.environ.get('SCAN_TIME', '10'))

targets = []
targets.append(PlugSwitchBotDevice)
targets.append(MeterSwitchBotDevice)
targets.append(BotSwitchBotDevice)
targets.append(ContactSwitchBotDevice)
targets.append(Hub2SwitchBotDevice)
targets.append(RemoteSwitchBotDevice)
targets.append(MeterProCO2SwitchBotDevice)

publisher = MQTTPublisher(HOST, PORT, TOPIC)

def detection_callback(device, advertisement_data):
    logger.debug(f"Detected device: address={device.address}, name={device.name}, rssi={advertisement_data.rssi}")
    
    for target in targets:
        info = target.parse(device, advertisement_data)
        if any(info):
            publisher.publish(device.address, device.name, advertisement_data.rssi, info)
            break

async def main():
    scanner = BleScanner(SCAN_TIME)
    while True:
        map = await scanner.scan()
        for key in map:
            entry = map[key]
            detection_callback(entry[0], entry[1])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

