import asyncio
import logging
from typing import List, Dict

import numpy as np
import websockets
import json
from datetime import datetime

from okx import Trade
from okx.websocket import WsUtils

from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE
from okx_market_maker.utils.LogFileEnum import LogFileEnum
from okx_market_maker.utils.LogUtil import LogUtil

logger = LogUtil(LogFileEnum.STRATEGY).get_logger()


class WbSocEXP:
    def __init__(self):
        # demo_api_key = "a134645d-747e-4d52-a5d0-36d3f1dbac21"
        # demo_secret = "72761FBA1C9BFF78014F38DD32C50D89"
        # demo_pass_phrase = "Xzy905097@1"
        # flag = "1"  # live trading: 0, demo trading: 1
        self.uri = "wss://wspap.okx.com:8443/ws/v5/private"
        self.trade_api = Trade.TradeAPI(API_KEY, API_KEY_SECRET, API_PASSPHRASE)
        self.loginPayload = WsUtils.initLoginParams(
            useServerTime=False,
            apiKey=API_KEY,
            passphrase=API_PASSPHRASE,
            secretKey=API_KEY_SECRET
        )

    async def okx_websocket_sub(self, channel, inst_id):
        args = self._prepare_args()
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(self.loginPayload)
            await asyncio.sleep(5)
            # 订阅BTC-USDT的实时交易数据（trade频道）
            subscribe_msg = {
                "op": "subscribe",
                "args": args
            }
            await websocket.send(json.dumps(subscribe_msg))
            logger.info(subscribe_msg)
            while True:
                try:
                    # 持续接收数据
                    async for message in websocket:
                        self.process_message(data=json.loads(message))
                except websockets.exceptions.ConnectionClosedError:
                    logger.error("WebSocket连接已关闭")
                    break

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

    def process_message(self, data):
        logger.warning(data)
        """解析tickers频道数据结构"""
        if 'event' in data:  # 忽略心跳响应
            return
        if data['arg']['channel'] == 'tickers':
            ticker = data['data'][0]
            okx_date_time = datetime.fromtimestamp((int)(ticker['ts']) / 1000)
            okx_inst_id = ticker['instId']
            okx_current_price = ticker['last']
            okx_24_vol = ticker['vol24h']
            okx_bid_px = ticker['bidPx']
            okx_ask_px = ticker['askPx']

            logger.debug(f"""
                    [{okx_date_time}]
                    交易对: {okx_inst_id}
                    最新价: {okx_current_price}
                    24小时成交量: {okx_24_vol}
                    买一价: {okx_bid_px}
                    卖一价: {okx_ask_px}
                    """)


# def init_grid(self , symbol , lower , upper , grid_num) :
#     prices = np.linspace ( lower , upper , grid_num + 1 )
#     for i in range ( grid_num ) :
#         self.trade_api.place_order ( symbol , 'buy' , prices [ i ] * 0.995 , grid_size )
#         self.trade_api.place_order ( symbol , 'sell' , prices [ i + 1 ] * 1.005 , grid_size )

if __name__ == "__main__":
    try:
        # data1 = {'arg': {'channel': 'tickers', 'instId': 'BTC-USDT'}, 'data': [{'instType': 'SPOT', 'instId': 'BTC-USDT', 'last': '103804', 'lastSz': '0.00009521', 'askPx': '103804.1', 'askSz': '0.84227986', 'bidPx': '103804', 'bidSz': '0.05854778', 'open24h': '103313.9', 'high24h': '107140.1', 'low24h': '103253.2', 'sodUtc0': '106468.9', 'sodUtc8': '105515.9', 'volCcy24h': '905690675.777423286', 'vol24h': '8640.85383751', 'ts': '1747626363874'}]}
        # process_message(data1)
        xx = WbSocEXP()
        asyncio.run(xx.okx_websocket_sub("tickers", "BTC-USDT"))
        logger.info("main函数执行成功！")
    except Exception as e:
        logger.error(f"Error: {e}")
