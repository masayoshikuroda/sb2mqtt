import sys
import logging
from bleak import BleakScanner
import asyncio

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

class BleScanner:
    def __init__(self, timeout=-1):
        self.timeout = timeout
    
    async def start(self, detection_callback):
        async with BleakScanner(timeout=self.timeout, detection_callback=detection_callback) as scanner:
            logger.info('scanner: created')
            await asyncio.sleep(self.timeout)
            logger.info('scanner: stopped')

    async def scan(self):
        async with BleakScanner(timeout=self.timeout) as scanner:
            logger.info('scanner: created')
            await asyncio.sleep(self.timeout)
            logger.info('scanner: stopped')
            return scanner.discovered_devices_and_advertisement_data     

def detection_callback(device, advertisement_data):
    logger.info(f"Detected device: address={device.address}, name={device.name}, rssi={advertisement_data.rssi}")
    logger.debug(f"    device: {device}")
    logger.debug(f"    Advertisement_data: rssi={advertisement_data.rssi}")
    logger.debug(f"        manufacturer_data: ")
    for uuid in advertisement_data.manufacturer_data:
        logger.debug(f"            {uuid}: {advertisement_data.manufacturer_data[uuid]}")
    logger.debug(f"        service_data: ")
    for uuid in advertisement_data.service_data:
            logger.debug(f"            {uuid}: {advertisement_data.service_data[uuid]}")

async def main():
    await BleScanner(10).start(detection_callback)

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(main())
