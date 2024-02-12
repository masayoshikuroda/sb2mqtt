import sys
import logging
from bleak import BleakScanner
import asyncio

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

class BleScanner:
    def __init__(self, sleep_time=-1):
        self.sleep_time  = sleep_time
    
    async def start(self, detection_callback):
        scanner = BleakScanner()
        logger.info('scanner: created')
        scanner.register_detection_callback(detection_callback)
        logger.info('scanner: registered')
        await scanner.start()
        logger.info('scanner: started')
        await asyncio.sleep(self.sleep_time)
        logger.info('scanner: slept')
        await scanner.stop()
        logger.info('scanner: stopped')
