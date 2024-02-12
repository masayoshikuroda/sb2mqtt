import sys
import logging

SERV_UUID = '0000fd3d-0000-1000-8000-00805f9b34fb'
CHAR_UUID = 2409

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

class SwitchBotDevice:
    def match(self, device, advertisement_data):
        if SERV_UUID not in advertisement_data.service_data:
            return False
        
        self.service_data = advertisement_data.service_data.get(SERV_UUID)
        self.device_type = self.service_data[0]
        logger.debug(f"Found SwitchBot device: type={hex(self.device_type)}")
        return True

class MeterSwitchBotDevice(SwitchBotDevice):
    def match(self, device, advertisement_data):
        if not super().match(device, advertisement_data):
            return False;
        if not self.device_type == 0x54:
            return False
        
        logger.info("Found SwitchBot Meter device")
        return True
    
    def parse(self, md):
        info = {}
        if CHAR_UUID not in md: 
            return info
        
        data = md[CHAR_UUID]
        info['device_id'] = data[0:6].hex().upper()
        info['device_type'] = 'meter'
        info['temperature']  = (data[9] & 0x7f) + (data[8] & 0x0f)/10
        info['humidity'] = (data[10] & 0x7f)
        return info
    
class PlugSwitchBotDevice(SwitchBotDevice):
    def match(self, device, advertisement_data):
        if not super().match(device, advertisement_data):
            return False;
        if not self.device_type == 0x67:
            return False
        
        logger.info("Found SwitchBot Plug device")
        return True
    
    def parse(self, md):
        info = {}
        if CHAR_UUID not in md: 
            return info
        
        data = md[CHAR_UUID]
        dts = data[8]
        info['device_id'] = data[0:6].hex().upper()
        info['rssi'] = data[9]
        info['device_type'] = 'plug'
        info['seq'] = data[6]
        info['status'] = 'on' if int.from_bytes(data[7:8], byteorder='little')==0x80 else 'off'
        info['delay'] = True if dts & 0x01 > 0 else False
        info['timer'] = True if dts & 0x02 > 0 else False
        info['sync_utc'] = True if dts & 0x04 > 0 else False
        info['overload'] = True if data[10] & 0xE0 > 0 else False
        info['power'] = int.from_bytes(data[10:12], byteorder='big') & 0x7FFF
        return info
