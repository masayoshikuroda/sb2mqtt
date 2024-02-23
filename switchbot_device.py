import sys
import logging
import asyncio
from ble_scanner import BleScanner 

SCAN_RSP = '0000fd3d-0000-1000-8000-00805f9b34fb'
ADV_IND = 2409

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

device_types = {
    0x48 : 'SwitchBot Bot (WoHand)',
    0x54 : 'SwitchBot MeterTH (WoSensorTH)/Normal',
    0x74 : 'SwitchBot MeterTH (WoSensorTH)/Add Mode',
    0x65 : 'SwitchBot Bot Humidifier',
    0x63 : 'SwitchBot Bot Curtain',
    0x73 : 'SwitchBot Bot MotionSensor',
    0x64 : 'SwitchBot Contact Sensor',
    0x75 : 'SwitchBot Color Bulb',
    0x72 : 'SwitchBot LED Strip Light',
    0x6F : 'SwitchBot Smart Lock',
    0x67 : 'SwitchBot Plug Mini',
    0x6A : 'SwitchBot Plug Mini(JP)',
    0x69 : 'SwitchBot Meter Plus',

    0x42 : 'WoButton',
    0x4C : 'SwitchBot Hub (WoLink)/Add Mode',
    0x6C : 'SwitchBot Hub (WoLink)/Normal',
    0x50 : 'SwitchBot Hub Plus (WoLink Plus)/Add Mode',
    0x70 : 'SwitchBot Hub Plus (WoLink Plus)/Normal Mode',
    0x46 : 'SwitchBot Fan (WoFan)/Add Mode',
    0x66 : 'SwitchBot Fan (WoFan)/Normal Mode',
    0x4D : 'SwitchBot Hub Mini (HubMini)/Add Mode',
    0x6D : 'SwitchBot Hub Mini (HubMini)/Normal Mode',

    0x76 : 'SwitchBot Hub 2',
    0x77 : 'SwitchBot MeterOutdoor(WoIOSensor)/w',
}

class SwitchBotDevice:
    def parse(device, advertisement_data):
        info = {}
        if SCAN_RSP not in advertisement_data.service_data:
            return {}
        
        service_data = advertisement_data.service_data.get(SCAN_RSP)
        device_type = service_data[0]
        device_name = device_types.get(device_type)

        manufacturer_data = advertisement_data.manufacturer_data
        data = manufacturer_data.get(ADV_IND)
        device_id = data[0:6].hex().upper()

        logger.debug(f"Found SwitchBot device: device_id={device_id}, type={hex(device_type)}({device_name})")
        return {'manufacture':'SwitchBot','service_data':service_data, 'device_type':device_type, 'device_id':device_id, 'data':data}
        
class BotSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x48:
            return {}
    
        info['model'] = 'WoBot'

        data = info['service_data']
        byte1 = data[1]
        info['mode']  = 'one state mode' if byte1 & 0x80 > 0 else 'on/off state mode'
        info['state']  = 'off' if byte1 & 0x40 > 0 else 'on'
        info['enc_type']  = '2 or 3' if byte1 & 0x20 > 0 else '0'
        info['data_commit_flag']  = 'no data update' if byte1 & 0x10 > 0 else 'has data update'
        info['group_d'] = True if byte1 & 0x08 > 0 else False
        info['group_c'] = True if byte1 & 0x04 > 0 else False
        info['group_b'] = True if byte1 & 0x02 > 0 else False
        info['group_a'] = True if byte1 & 0x01 > 0 else False
        byte2 = data[1]
        info['sync_utc']  = True if byte2& 0x80 > 0 else False
        info['battery']  = byte2 & 0x7f

        logger.info(f"Found SwitchBot Bot device: device_id={info['device_id']}, mode={info['mode']}, state={info['state']}")
        return info
        
class MeterSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x54:
            return {}
        
        info['model'] = 'WoSensorTH'

        data = info['data']
        service_data = info['service_data']
        byte0 = service_data[0]

        byte1 = service_data[1]
        info['group_d'] = True if byte1 & 0x08 > 0 else False
        info['group_c'] = True if byte1 & 0x04 > 0 else False
        info['group_b'] = True if byte1 & 0x02 > 0 else False
        info['group_a'] = True if byte1 & 0x01 > 0 else False       
        byte2 = service_data[2]
        info['battery'] = byte2 & 0x7f
        byte3 = service_data[3]
        info['temperature_alart_status'] = byte3 & 0xc0
        info['humidity_alert_status'] = byte3 & 0x30
        byte4 = service_data[4]
        info['temperature'] = (byte4 & 0x7f) + (byte3 & 0x0f)/10
        byte5 = service_data[5]
        info['humidity'] = (byte5 & 0x7f)

        logger.info(f"Found SwitchBot Sensor device: device_id={info['device_id']}, temperature={info['temperature']}, humidity={info['humidity']}")
        return info
    
class PlugSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x67 and not info['device_type'] == 0x6A:
            return {}
        
        info['model'] = 'WoPlug'

        data = info['data']
        info['seq'] = data[6]
        info['status'] = 'on' if int.from_bytes(data[7:8], byteorder='little')==0x80 else 'off'
        info['delay'] = True if data[8] & 0x01 > 0 else False
        info['timer'] = True if data[8] & 0x02 > 0 else False
        info['sync_utc']= True if data[8] & 0x04 > 0 else False
        info['rssi'] = data[9]
        info['overload'] = True if data[10] & 0xE0 > 0 else False
        info['power'] = (int.from_bytes(data[10:12], byteorder='big') & 0x7FFF)/ 10

        logger.info(f"Found SwitchBot Plug device: device_id={info['device_id']}, status={info['status']}, power={info['power']}")
        return info

class MotionSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x64:
            return {}
        
        info['model'] = 'WoContact'

        service_data = info['service_data']
        byte2 = service_data[2]
        info['battery'] = byte2 & 0x7f 

        logger.info(f"Found SwitchBot Motion device: device_id={info['device_id']}, battery={info['battery']}")
        return info     

def detection_callback(device, advertisement_data):
    info = MotionSwitchBotDevice.parse(device, advertisement_data)
    if any(info):
        logger.info(info)

async def main():
    await BleScanner(10).start(detection_callback)

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(main())