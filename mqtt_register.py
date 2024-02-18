import sys
import logging
import json
from datetime import datetime
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

TOPIC = 'ble2mqtt'

def on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f"Connected with result code {reason_code}")

class MQTTRegister:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = on_connect
        self.client.connect(host, port)

    def regist(self, address, name, rssi, info):
        delete_keys = []
        for key in info.keys():
            if type(info[key]) is bytes:
                delete_keys.append(key)
        for key in delete_keys:
            info.pop(key)

        info['last_update'] = datetime.now().strftime('%Y-%m-%d %H:hon%M:%S.%f')
        info['device_name'] = name
        info['rssi'] = rssi
        
        topic = f"{TOPIC}/{address}/info"
        data = json.dumps(info, ensure_ascii=False)
        self.client.publish(topic, data)
        logger.info(f"Published device information. topic={topic}")