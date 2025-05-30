import asyncio
import json
import logging
import time
from logging import DEBUG
from typing import List, Dict

from okx_market_maker.position_management_service.model.BalanceAndPosition import BalanceAndPosition, \
    BalanceData, PosData
from okx_market_maker.position_management_service.model.Account import Account, AccountDetail
from okx_market_maker.position_management_service.model.Positions import Position, Positions
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx_market_maker import balance_and_position_container, account_container, positions_container, wait_consume_second
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE
from okx_market_maker.utils.LogFileEnum import LogFileEnum
from okx_market_maker.utils.LogUtil import LogUtil

# 创建logger
logger = LogUtil(LogFileEnum.POSITION).get_logger()


class WssPositionManagementService(WsPrivateAsync):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
        self.args = []

    # async def start(self):
    #     logger.info("Connecting to WebSocket...")
    #     await self.connect()

    async def run_service(self):
        logger.info("position management subscribing ...")
        await self.start()
        args = self._prepare_args()
        logger.info(f"position subscribe args: {args}")
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
        account_sub = {
            "channel": "account"
        }
        args.append(account_sub)
        positions_sub = {
            "channel": "positions",
            "instType": "ANY"
        }
        args.append(positions_sub)
        balance_and_position_sub = {
            "channel": "balance_and_position"
        }
        args.append(balance_and_position_sub)
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
    # if not msgJson['event'] or msgJson['event'] == "subscribe":
    #     return
    if arg['channel'] == "balance_and_position":
        on_balance_and_position(msgJson)
    if arg['channel'] == "account":
        on_account(msgJson)
    if arg['channel'] == "positions":
        on_position(msgJson)


def on_balance_and_position(message):
    if not balance_and_position_container:
        balance_and_position_container.append(BalanceAndPosition.init_from_json(message))
    else:
        balance_and_position_container[0].update_from_json(message)
    logger.debug(f"show balance_and_position_container:{balance_and_position_container}")


def on_account(message):
    if not account_container:
        account_container.append(Account.init_from_json(message))
    else:
        account_container[0].update_from_json(message)
    logger.debug(f"show account_container:{account_container}")


def on_position(message):
    if not positions_container:
        positions_container.append(Positions.init_from_json(message))
    else:
        positions_container[0].update_from_json(message)
    logger.debug(f"show positions_container:{positions_container}")


if __name__ == "__main__":
    uri = "wss://wspap.okx.com:8443/ws/v5/private"
    position_management_service = WssPositionManagementService(url=uri)
    asyncio.run(position_management_service.start())
    asyncio.run(position_management_service.run_service())
    time.sleep(30)
