import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List

from okx_market_maker import order_books
from okx_market_maker.market_data_service.model.OrderBook import OrderBook, OrderBookLevel
from okx.websocket.WsPublicAsync import WsPublicAsync

# 获取项目根目录
project_dir = os.path.dirname(os.path.dirname(__file__))
# 配置日志文件路径
current_file_path = os.path.join(project_dir, 'logs', 'market-date-service.log')
# os.makedirs(current_file_path, exist_ok=True)

logger = logging.getLogger(__name__)
defaultLogger = logging.getLogger()

# 创建当前类日志文件的Handler
current_class_file_handler = logging.FileHandler(current_file_path)
current_class_file_handler.setLevel(logging.INFO)
# 创建第三方包日志文件的Handler
third_party_file_handler = logging.FileHandler('default.log')
third_party_file_handler.setLevel(logging.INFO)
#创建控制台handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
third_party_file_handler.setFormatter(formatter)
current_class_file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
# logger.addHandler(current_class_file_handler)
# defaultLogger.addHandler(third_party_file_handler)


class WssMarketDataService(WsPublicAsync):
    def __init__(self, url, inst_id, channel="books5"):
        super().__init__(url)
        self.inst_id = inst_id
        self.channel = channel
        order_books[self.inst_id] = OrderBook(inst_id=inst_id)
        self.args = []

    # async def subscribe(self, params: list, callback):
    #     print("process in subscribing...")
    #     self.callback = callback
    #     payload = json.dumps({
    #         "op": "subscribe",
    #         "args": params
    #     })
    #     await self.websocket.send(payload)
    #     print(f"websocket info:{self.websocket}")
    #     self.loop.create_task(self.consume())
    #
    # async def consume(self):
    #     print("process in consuming...")
    #     async for message in self.websocket:
    #         print("Received message: {%s}", message)
    #         _callback(message)
    #
    # async def start(self):
    #     print("process in starting...")
    #     await self.connect()
    #     print(f"socketId:{self.websocket.id}===socketState:{self.websocket.state}")

    async def run_service(self):
        logger.info("process in run_service...")
        args = self._prepare_args()
        logger.info(f"subscribe args: {args}")
        await self.subscribe(args, _callback)
        self.args += args

    # async def okx_websocket_sub(self):
    #     async with websockets.connect(self.url) as websocket:
    #         # 订阅BTC-USDT的实时交易数据（trade频道）
    #         subscribe_msg = {
    #             "op": "subscribe",
    #             "args": [{"channel": self.channel, "instId": self.inst_id}]
    #         }
    #         await websocket.send(json.dumps(subscribe_msg))
    #         print(subscribe_msg)
    #         while True:
    #             try:
    #                 # 持续接收数据
    #                 async for message in websocket:
    #                     _callback(message)
    #             except websockets.exceptions.ConnectionClosedError:
    #                 print("WebSocket连接已关闭")
    #                 break

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: logger.info(message))
        self.close()

    def _prepare_args(self) -> List[Dict]:
        args = []
        books5_sub = {
            "channel": self.channel,
            "instId": self.inst_id
        }
        args.append(books5_sub)
        return args


def _callback(message):
    logger.info(message)
    data = json.loads(message)
    arg = data['arg']
    if not arg or not arg['channel']:
        return
    if 'event' in data:  # 忽略心跳响应
        return
    if arg['channel'] in ["tickers"]:
        on_ticker_data(data['data'])
    if arg['channel'] in ["books5", "books", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"]:
        on_orderbook_snapshot_or_update(data)
        # print(order_books)


def on_ticker_data(data):
    ticker = data[0]
    okx_date_time = datetime.fromtimestamp((int)(ticker['ts']) / 1000)
    okx_inst_id = ticker['instId']
    okx_current_price = ticker['last']
    okx_24_vol = ticker['vol24h']
    okx_bid_px = ticker['bidPx']
    okx_ask_px = ticker['askPx']

    print(f"""
            [{okx_date_time}]
                    交易对: {okx_inst_id}
                    最新价: {okx_current_price}
                    24小时成交量: {okx_24_vol}
                    买一价: {okx_bid_px}
                    卖一价: {okx_ask_px}
                    """)


def on_orderbook_snapshot_or_update(message):
    """
    :param message:
    {
    "arg": {
        "channel": "books",
        "instId": "BTC-USDT"
    },
    "action": "snapshot",
    "data": [{
        "asks": [
            ["8476.98", "415", "0", "13"],
            ["8477", "7", "0", "2"],
            ["8477.34", "85", "0", "1"],
            ["8477.56", "1", "0", "1"],
            ["8505.84", "8", "0", "1"],
            ["8506.37", "85", "0", "1"],
            ["8506.49", "2", "0", "1"],
            ["8506.96", "100", "0", "2"]
        ],
        "bids": [
            ["8476.97", "256", "0", "12"],
            ["8475.55", "101", "0", "1"],
            ["8475.54", "100", "0", "1"],
            ["8475.3", "1", "0", "1"],
            ["8447.32", "6", "0", "1"],
            ["8447.02", "246", "0", "1"],
            ["8446.83", "24", "0", "1"],
            ["8446", "95", "0", "3"]
        ],
        "ts": "1597026383085",
        "checksum": -855196043
    }]
}
    :return:
    """
    arg = message.get("arg")
    inst_id = arg.get("instId")
    action = message.get("action")
    if inst_id not in order_books:
        order_books[inst_id] = OrderBook(inst_id=inst_id)
    data = message.get("data")[0]
    if data.get("asks"):
        if action == "snapshot" or not action:
            ask_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["asks"]]
            order_books[inst_id].set_asks_on_snapshot(ask_list)
        if action == "update":
            for level_info in data["asks"]:
                order_books[inst_id].set_asks_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("bids"):
        if action == "snapshot" or not action:
            bid_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["bids"]]
            order_books[inst_id].set_bids_on_snapshot(bid_list)
        if action == "update":
            for level_info in data["bids"]:
                order_books[inst_id].set_bids_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("ts"):
        order_books[inst_id].set_timestamp(int(data["ts"]))
    if data.get("checksum"):
        order_books[inst_id].set_exch_check_sum(data["checksum"])


class ChecksumThread(threading.Thread):
    def __init__(self, wss_mds: WssMarketDataService):
        self.wss_mds = wss_mds
        super().__init__()

    def run(self) -> None:
        while 1:
            try:
                for inst_id, order_book in order_books.items():
                    order_book: OrderBook
                    if order_book.do_check_sum():
                        continue
                    self.wss_mds.stop_service()
                    time.sleep(3)
                    self.wss_mds.run_service()
                    break
                time.sleep(5)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    # url = "wss://ws.okx.com:8443/ws/v5/public"
    url = "wss://ws.okx.com:8443/ws/v5/public"
    market_data_service = WssMarketDataService(url=url, inst_id="BTC-USDT", channel="books")
    asyncio.run(market_data_service.start())
    asyncio.run(market_data_service.run_service())
    # asyncio.run(market_data_service.okx_websocket_sub())
    # asyncio.run(market_data_service.consume())
    check_sum = ChecksumThread(market_data_service)
    check_sum.start()
