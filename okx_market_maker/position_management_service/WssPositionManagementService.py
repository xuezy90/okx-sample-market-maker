import asyncio
import json
import logging
import time
from typing import List, Dict
import copy

from okx_market_maker.position_management_service.model.BalanceAndPosition import BalanceAndPosition, \
    BalanceData, PosData
from okx_market_maker.position_management_service.model.Account import Account, AccountDetail
from okx_market_maker.position_management_service.model.Positions import Position, Positions
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx_market_maker import balance_and_position_container, account_container, positions_container
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class WssPositionManagementService(WsPrivateAsync):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
        self.args = []

    async def run_service(self):
        args = self._prepare_args()
        logger.info(f"position subscribe args: {args}")
        logger.info("position management subscribing ...")
        await self.subscribe(args, _callback)
        self.args += args

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
    logger.info(message)
    data = json.loads(message)
    if 'arg' not in data:
        return
    arg = data['arg']
    if not arg or not arg['channel']:
        return
    if data['event'] == "subscribe":
        return
    if arg['channel'] == "balance_and_position":
        logger.info(f"balance and position result:{message}")
        on_balance_and_position(message)
        logger.info(f"balance and position container:{balance_and_position_container}")
    if arg['channel'] == "account":
        logger.info(f"account result:{message}")
        on_account(message)
        logger.info(f"account container:{account_container}")
    if arg['channel'] == "positions":
        logger.info(f"positions result:{message}")
        on_position(message)
        logger.info(f"positions container:{positions_container}")


def on_balance_and_position(message):
    if not balance_and_position_container:
        balance_and_position_container.append(BalanceAndPosition.init_from_json(message))
    else:
        balance_and_position_container[0].update_from_json(message)


def on_account(message):
    if not account_container:
        account_container.append(Account.init_from_json(message))
    else:
        account_container[0].update_from_json(message)


def on_position(message):
    if not positions_container:
        positions_container.append(Positions.init_from_json(message))
    else:
        positions_container[0].update_from_json(message)


if __name__ == "__main__":
    url = "wss://ws.okx.com:8443/ws/v5/private"
    position_management_service = WssPositionManagementService(url=url)
    asyncio.run(position_management_service.start())
    asyncio.run(position_management_service.run_service())
    time.sleep(30)
