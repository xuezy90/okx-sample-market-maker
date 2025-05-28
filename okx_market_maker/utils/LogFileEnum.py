from enum import Enum


class LogFileEnum(Enum):
    MARKET = "market"
    ORDER = "order"
    POSITION = "position"
    STRATEGY = "strategy"