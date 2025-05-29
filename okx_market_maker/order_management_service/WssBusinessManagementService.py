import asyncio
import json
import time
from typing import List, Dict

from okx_market_maker.order_management_service.model.Order import Order, Orders
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx_market_maker import orders_container, wait_consume_second
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE
from okx_market_maker.utils.LogFileEnum import LogFileEnum
from okx_market_maker.utils.LogUtil import LogUtil

# 创建logger
logger = LogUtil(LogFileEnum.ORDER).get_logger()


class WssBusinessManagementService(WsPrivateAsync):
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
        logger.info(f"subscribe args: {args}")
        await self.subscribe(args, _callback)
        # await self.consume()
        self.args += args
        await asyncio.sleep(wait_consume_second)

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: logger.info(message))
        self.close()

    @staticmethod
    def _prepare_args() -> List[Dict]:
        args = []
        # 策略交易
        orders_sub1 = {
            "channel": "orders-algo",
            "instType": "ANY",
        }
        args.append(orders_sub1)
        # 网格现货交易
        orders_sub2 = {
            "channel": "grid-orders-spot",
            "instType": "ANY",
        }
        args.append(orders_sub2)
        # 策略期货交易
        orders_sub3 = {
            "channel": "grid-orders-contract",
            "instType": "ANY",
        }
        args.append(orders_sub3)
        # 定投交易
        orders_sub4 = {
            "channel": "algo-recurring-buy",
            "instType": "ANY",
        }
        args.append(orders_sub4)
        return args


def _callback(message):
    logger.debug(message)


if __name__ == "__main__":
    # url = "wss://ws.okx.com:8443/ws/v5/private"
    url = "wss://wspap.okx.com:8443/ws/v5/business"
    order_management_service = WssBusinessManagementService(url=url)
    asyncio.run(order_management_service.start())
    asyncio.run(order_management_service.run_service())
    time.sleep(30)
