import asyncio
import json
import time
from typing import List, Dict

from okx_market_maker.order_management_service.model.Order import Order, Orders
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx_market_maker import orders_container
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE
from okx_market_maker.utils.LogFileEnum import LogFileEnum
from okx_market_maker.utils.LogUtil import LogUtil

# 创建logger
logger = LogUtil(LogFileEnum.ORDER).get_logger()

class WssOrderManagementService(WsPrivateAsync):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
        self.args = []
    # async def start(self):
    #     logger.info("Connecting to WebSocket...")
    #     await self.connect()
    #     # self.loop.create_task(self.consume())

    async def run_service(self):
        logger.info("process in run_service...")
        await self.start()
        args = self._prepare_args()
        logger.info(args)
        orders_container.append(Orders())
        logger.info(f"subscribe args: {args}")
        await self.subscribe(args, _callback)
        # await self.consume()
        self.args += args

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: logger.info(message))
        self.close()

    @staticmethod
    def _prepare_args() -> List[Dict]:
        args = []
        orders_sub = {
            "channel": "orders",
            "instType": "ANY",
        }
        args.append(orders_sub)
        return args


def _callback(message):
    logger.debug(message)
    msgJson = json.loads(message)
    if 'arg' not in msgJson:
        return
    arg = msgJson['arg']
    if not arg or not arg['channel']:
        return
    if 'data' not in msgJson:
        return
    if not msgJson['data']:
        return

    if arg['channel'] == "orders":
        on_orders_update(msgJson)

    logger.info(f"orders_container: {orders_container}")

def on_orders_update(message):
    if not orders_container:
        orders_container.append(Orders.init_from_json(message))
    else:
        orders_container[0].update_from_json(message)
    logger.info(orders_container)


if __name__ == "__main__":
    # url = "wss://ws.okx.com:8443/ws/v5/private"
    url = "wss://ws.okx.com:8443/ws/v5/private?brokerId=9999"
    order_management_service = WssOrderManagementService(url=url)
    asyncio.run(order_management_service.start())
    asyncio.run(order_management_service.run_service())
    time.sleep(30)
