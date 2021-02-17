"""Driver for auto_trader_client"""


import src.client_utils as utils
from src.client_settings import (
    ROOT_LOG,
    LOG_DIR,
    GCP_CREDS_PATH,
    DEFAULT_ORDER_DIR,
    BUCKET_NAMES_PATH,
    BUCKET_DICT_KEY,
)
import asyncio
import json
import src.bucket_listener as bl
import src.order_monitor as om


async def start_workers(bucket_name):
    await asyncio.gather(
        bl.BucketListener(bucket_name, GCP_CREDS_PATH, DEFAULT_ORDER_DIR).run(),
        om.OrderMonitor(DEFAULT_ORDER_DIR).run(),
    )


async def main():
    # initiate logger
    utils.init_root_logger(ROOT_LOG, LOG_DIR)

    # get bucket name
    with open(BUCKET_NAMES_PATH) as fp:
        bucket_name = json.load(fp)[BUCKET_DICT_KEY]

    # start workers
    await start_workers(bucket_name)


if __name__ == "__main__":
    asyncio.run(main())
