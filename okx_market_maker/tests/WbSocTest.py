import asyncio

import numpy as np
import websockets
import json
from datetime import datetime

from okx import Trade

class WbSocEXP :
    def __init__(self) :
        demo_api_key = "a134645d-747e-4d52-a5d0-36d3f1dbac21"
        demo_secret = "72761FBA1C9BFF78014F38DD32C50D89"
        demo_pass_phrase = "Xzy905097@1"
        flag = "1"  # live trading: 0, demo trading: 1
        self.uri = "wss://ws.okx.com:8443/ws/v5/public"
        self.trade_api = Trade.TradeAPI ( demo_api_key , demo_secret , demo_pass_phrase , flag )


    async def okx_websocket_sub(self , channel , inst_id) :
        async with websockets.connect ( self.uri ) as websocket :
            # 订阅BTC-USDT的实时交易数据（trade频道）
            subscribe_msg = {
                "op" : "subscribe" ,
                "args" : [ {"channel" : channel , "instId" : inst_id} ]
            }
            await websocket.send ( json.dumps ( subscribe_msg ) )
            print ( subscribe_msg )
            while True :
                try :
                    # 持续接收数据
                    async for message in websocket :
                        self.process_message ( data=json.loads ( message ) )
                except websockets.exceptions.ConnectionClosedError :
                    print ( "WebSocket连接已关闭" )
                    break


    def process_message(self , data) :
        print ( data )
        """解析tickers频道数据结构"""
        if 'event' in data :  # 忽略心跳响应
            return
        if data [ 'arg' ] [ 'channel' ] == 'tickers' :
            ticker = data [ 'data' ] [ 0 ]
            okx_date_time = datetime.fromtimestamp ( (int) ( ticker [ 'ts' ] ) / 1000 )
            okx_inst_id = ticker [ 'instId' ]
            okx_current_price = ticker [ 'last' ]
            okx_24_vol = ticker [ 'vol24h' ]
            okx_bid_px = ticker [ 'bidPx' ]
            okx_ask_px = ticker [ 'askPx' ]

            print ( f"""
                    [{okx_date_time}]
                    交易对: {okx_inst_id}
                    最新价: {okx_current_price}
                    24小时成交量: {okx_24_vol}
                    买一价: {okx_bid_px}
                    卖一价: {okx_ask_px}
                    """ )


# def init_grid(self , symbol , lower , upper , grid_num) :
#     prices = np.linspace ( lower , upper , grid_num + 1 )
#     for i in range ( grid_num ) :
#         self.trade_api.place_order ( symbol , 'buy' , prices [ i ] * 0.995 , grid_size )
#         self.trade_api.place_order ( symbol , 'sell' , prices [ i + 1 ] * 1.005 , grid_size )

if __name__ == "__main__" :
    try :
        # data1 = {'arg': {'channel': 'tickers', 'instId': 'BTC-USDT'}, 'data': [{'instType': 'SPOT', 'instId': 'BTC-USDT', 'last': '103804', 'lastSz': '0.00009521', 'askPx': '103804.1', 'askSz': '0.84227986', 'bidPx': '103804', 'bidSz': '0.05854778', 'open24h': '103313.9', 'high24h': '107140.1', 'low24h': '103253.2', 'sodUtc0': '106468.9', 'sodUtc8': '105515.9', 'volCcy24h': '905690675.777423286', 'vol24h': '8640.85383751', 'ts': '1747626363874'}]}
        # process_message(data1)
        xx = WbSocEXP()
        asyncio.run ( xx.okx_websocket_sub("tickers" , "BTC-USDT" ))
        print ( "main函数执行成功！" )
    except Exception as e :
        print ( f"Error: {e}" )
    finally :
        print ( "===main函数执行完毕！==" )
