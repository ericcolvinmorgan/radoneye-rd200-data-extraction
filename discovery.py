import asyncio
import logging
import sys
from bleak import BleakClient, BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

address = "E8:31:CD:CD:EC:E2"
HISTORY_REQUEST_UUID = "00001524-0000-1000-8000-00805f9b34fb"
HISTORY_NOTIFY_UUID = "00001526-0000-1000-8000-00805f9b34fb"
UNKNOWN_NOTIFY_UUID = "00001525-0000-1000-8000-00805f9b34fb"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

async def main(address):
    async with BleakClient(address) as client:
        for service in client.services:
            logger.info("[Service] %s", service)

            for char in service.characteristics:
                logger.info(char)
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        logger.info(
                            "  [Characteristic] %s (%s), Value: %r",
                            char,
                            ",".join(char.properties),
                            value,
                        )
                    except Exception as e:
                        logger.error(
                            "  [Characteristic] %s (%s), Error: %s",
                            char,
                            ",".join(char.properties),
                            e,
                        )

                else:
                    logger.info(
                        "  [Characteristic] %s (%s)", char, ",".join(char.properties)
                    )

                for descriptor in char.descriptors:
                    try:
                        value = await client.read_gatt_descriptor(descriptor.handle)
                        logger.info("    [Descriptor] %s, Value: %r", descriptor, value)
                    except Exception as e:
                        logger.error("    [Descriptor] %s, Error: %s", descriptor, e)

        async def notification_handler(characteristic, data):
            print(f"{characteristic}: {data.hex()}")

        # await client.write_gatt_char(HISTORY_REQUEST_UUID, bytearray([0xa1]))
        # await asyncio.sleep(.5)
        # await client.write_gatt_char(HISTORY_REQUEST_UUID, bytearray([0xa1]))
        # await asyncio.sleep(.5)
        # await client.write_gatt_char(HISTORY_REQUEST_UUID, bytearray([0xa1]))
        # await asyncio.sleep(.5)


        await client.start_notify(UNKNOWN_NOTIFY_UUID, notification_handler)
        await client.start_notify(HISTORY_NOTIFY_UUID, notification_handler)
        
        # for i in range(0x4a, 0xff + 1):
        i = 0x41
        logger.info(f"Testing Write Value: {hex(i)}")
        await client.write_gatt_char(HISTORY_REQUEST_UUID, bytearray([i]))
        await asyncio.sleep(1.0)
        
        # await client.stop_notify(HISTORY_NOTIFY_UUID)


asyncio.run(main(address))
