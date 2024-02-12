import sys
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

TOPIC = 'ble2mqtt'

class MQTTRegister:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = mqtt.Client()
        self.client.connect(host, port)
        logger.info(f"Connected MQTT broker. host={host}, port={port}")

    def regist(self, address, name, rssi, info):
        info['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        info['device_name'] = name
        info['rssi'] = rssi
        self.client.publish(f"{TOPIC}/{address}/info", str(info))
        logger.info(f"Published device information. address={address}, name={name}")