import asyncio

from okx_market_maker.strategy.SampleMM import SampleMM


if __name__ == "__main__":
    strategy = SampleMM()
    asyncio.run(strategy.run())

