import sys
import time
import logging
import json
from datetime import datetime
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f"Connected with result code {reason_code}")

def on_disconnect(client, userdata, rc):
    logger.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logger.info("Reconnected successfully!")
            return
        except Exception as err:
            logger.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logger.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

class MQTTPublisher:
    def __init__(self, host, port, topic):
        self.host = host
        self.port = port
        self.topic = topic
        logger.info(f"MQTT host={host}, port={port} topic={topic}")
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except:
            elf.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.connect(host, port)

    def publish(self, address, name, rssi, info):
        delete_keys = []
        for key in info.keys():
            if type(info[key]) is bytes:
                delete_keys.append(key)
                logger.debug(f"Deleted key={key}, value={info[key]}")
        for key in delete_keys:
            info.pop(key)

        info['address'] = address
        info['name'] = name
        info['rssi'] = rssi
        info['update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        topic = f"{self.topic}/{address}/info"
        data = json.dumps(info, ensure_ascii=False)
        self.client.publish(topic, data)
        logger.info(f"Published device information. topic={topic}")
