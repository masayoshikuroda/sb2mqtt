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
    0x62 : 'SwitchBot Remote',
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

    0x35 : 'SwitchBot MeterPro(CO2)'
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
        return {'address': device.address, 'manufacture':'SwitchBot','service_data':service_data, 'device_type':device_type, 'device_id':device_id, 'data':data}
        
class BotSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x48:
            return {}
    
        info['model'] = 'WoHand'

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
        if info['device_type'] == 0x54:
            info['model'] = 'WoSensorTH'
        elif info['device_type'] == 0x77:
            info['model'] = 'WoIOSensorTH'
        else:
            return {}
        
        bytes = info['data'][5:]
        info['group_d'] = True if bytes[1] & 0x08 > 0 else False
        info['group_c'] = True if bytes[1] & 0x04 > 0 else False
        info['group_b'] = True if bytes[1] & 0x02 > 0 else False
        info['group_a'] = True if bytes[1] & 0x01 > 0 else False       
        info['battery'] = bytes[2] & 0x7f
        info['temperature_alart_status'] = bytes[3] & 0xc0
        info['humidity_alert_status'] = bytes[3] & 0x30
        info['temperature'] = (bytes[4] & 0x7f) + (bytes[3] & 0x0f)/10
        info['humidity'] = (bytes[5] & 0x7f)

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

        bytes = b"\x09\x69" + info['data']
        info['seq'] = bytes[8]
        info['status'] = 'on' if int.from_bytes(bytes[9:10], byteorder='little')==0x80 else 'off'
        info['delay'] = True if bytes[10] & 0x01 > 0 else False
        info['timer'] = True if bytes[10] & 0x02 > 0 else False
        info['sync_utc']= True if bytes[10] & 0x04 > 0 else False
        info['rssi'] = bytes[11]
        info['overload'] = True if bytes[12] & 0xE0 > 0 else False
        info['power'] = (int.from_bytes(bytes[12:14], byteorder='big') & 0x7FFF)/ 10

        logger.info(f"Found SwitchBot Plug device: device_id={info['device_id']}, status={info['status']}, power={info['power']}")
        return info

class ContactSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x64:
            return {}
        
        info['model'] = 'WoContact'

        bytes = info['service_data']
        info['battery'] = bytes[2] & 0x7f 

        logger.info(f"Found SwitchBot Motion device: device_id={info['device_id']}, battery={info['battery']}")
        return info

class Hub2SwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x76:
            return {}

        info['model'] = 'WoHub2'

        bytes = info['data'][10:]
        info['temperature'] = (bytes[4] & 0x7f) + (bytes[3] & 0x0f)/10
        info['humidity'] = (bytes[5] & 0x7f)

        logger.info(f"Found SwitchBot Hub2 device: device_id={info['device_id']}")
        return info
    
class RemoteSwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x62:
            return {}

        info['model'] = 'WoRemote'

        bytes = info['data'][6:]

        info['data_suffix'] = bytes

        logger.info(f"Found SwitchBot Remote device: device_id={info['device_id']}")
        return info        

class MeterProCO2SwitchBotDevice:
    def parse(device, advertisement_data):
        info = SwitchBotDevice.parse(device, advertisement_data)
        if not any(info):
            return {}
        if not info['device_type'] == 0x35:
            return {}

        info['model'] = 'WoTHPc'

        bytes = info['data'][5:]
        info['group_d'] = True if bytes[1] & 0x08 > 0 else False
        info['group_c'] = True if bytes[1] & 0x04 > 0 else False
        info['group_b'] = True if bytes[1] & 0x02 > 0 else False
        info['group_a'] = True if bytes[1] & 0x01 > 0 else False
        info['battery'] = bytes[2] & 0x7f
        info['temperature_alart_status'] = bytes[3] & 0xc0
        info['humidity_alert_status'] = bytes[3] & 0x30
        info['temperature'] = (bytes[4] & 0x7f) + (bytes[3] & 0x0f)/10
        info['humidity'] = (bytes[5] & 0x7f)
        info['co2'] = int.from_bytes(bytes[8:10], byteorder='big') 

        logger.info(f"Found SwitchBot Meter Pro(CO2) device: device_id={info['device_id']}")
        return info

def detection_callback(device, advertisement_data):
    info = SwitchBotDevice.parse(device, advertisement_data)
    if any(info):
        logger.info(info)

async def main():
    await BleScanner(60).start(detection_callback)

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(main())
