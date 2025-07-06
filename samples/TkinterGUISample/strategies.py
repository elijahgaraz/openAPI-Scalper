import random
from dataclasses import dataclass
from typing import Callable, Dict

from twisted.internet.task import LoopingCall

from ctrader_open_api.messages.OpenApiMessages_pb2 import (
    ProtoOANewOrderReq,
    ProtoOAOrderType,
    ProtoOATradeSide,
)


# Example mapping of symbols to numeric identifiers.
# Actual IDs vary by broker and should be replaced accordingly.
SYMBOL_IDS: Dict[str, int] = {
    "EURUSD": 1,
    "GBPUSD": 2,
    "USDJPY": 3,
    "AUDUSD": 4,
    "USDCHF": 5,
}


def evaluate_market(pair: str) -> str:
    """Placeholder for future AI driven signal generation."""
    return random.choice(["BUY", "SELL"])


# Individual strategy implementations


def safe(client, account_id: int, pair: str, log: Callable[[str], None]):
    direction = evaluate_market(pair)
    req = ProtoOANewOrderReq()
    req.ctidTraderAccountId = int(account_id)
    req.symbolId = SYMBOL_IDS[pair]
    req.orderType = ProtoOAOrderType.MARKET
    req.tradeSide = ProtoOATradeSide.Value(direction)
    req.volume = 10 * 100  # 0.1 lot
    d = client.send(req)
    d.addCallbacks(lambda _: log(f"Safe {direction} order sent"), lambda f: log(str(f)))


def moderate(client, account_id: int, pair: str, log: Callable[[str], None]):
    direction = evaluate_market(pair)
    req = ProtoOANewOrderReq()
    req.ctidTraderAccountId = int(account_id)
    req.symbolId = SYMBOL_IDS[pair]
    req.orderType = ProtoOAOrderType.MARKET
    req.tradeSide = ProtoOATradeSide.Value(direction)
    req.volume = 50 * 100  # 0.5 lot
    d = client.send(req)
    d.addCallbacks(lambda _: log(f"Moderate {direction} order sent"), lambda f: log(str(f)))


def aggressive(client, account_id: int, pair: str, log: Callable[[str], None]):
    direction = evaluate_market(pair)
    req = ProtoOANewOrderReq()
    req.ctidTraderAccountId = int(account_id)
    req.symbolId = SYMBOL_IDS[pair]
    req.orderType = ProtoOAOrderType.MARKET
    req.tradeSide = ProtoOATradeSide.Value(direction)
    req.volume = 100 * 100  # 1 lot
    d = client.send(req)
    d.addCallbacks(lambda _: log(f"Aggressive {direction} order sent"), lambda f: log(str(f)))


def trends(client, account_id: int, pair: str, log: Callable[[str], None]):
    direction = evaluate_market(pair)
    req = ProtoOANewOrderReq()
    req.ctidTraderAccountId = int(account_id)
    req.symbolId = SYMBOL_IDS[pair]
    req.orderType = ProtoOAOrderType.MARKET
    req.tradeSide = ProtoOATradeSide.Value(direction)
    req.volume = 20 * 100  # 0.2 lot
    d = client.send(req)
    d.addCallbacks(lambda _: log(f"Trend {direction} order sent"), lambda f: log(str(f)))


def scalping(client, account_id: int, pair: str, log: Callable[[str], None]):
    direction = evaluate_market(pair)
    req = ProtoOANewOrderReq()
    req.ctidTraderAccountId = int(account_id)
    req.symbolId = SYMBOL_IDS[pair]
    req.orderType = ProtoOAOrderType.MARKET
    req.tradeSide = ProtoOATradeSide.Value(direction)
    req.volume = 5 * 100  # 0.05 lot
    d = client.send(req)
    d.addCallbacks(lambda _: log(f"Scalping {direction} order sent"), lambda f: log(str(f)))


STRATEGIES: Dict[str, Callable[[object, int, str, Callable[[str], None]], None]] = {
    "safe": safe,
    "moderate": moderate,
    "aggressive": aggressive,
    "trends": trends,
    "scalping": scalping,
}


@dataclass
class StrategyManager:
    client: object
    account_id: int
    log: Callable[[str], None]
    _loop: LoopingCall = None

    def start(self, name: str, pair: str) -> None:
        self.stop()
        func = STRATEGIES.get(name.lower())
        if not func:
            self.log(f"Unknown strategy: {name}")
            return
        self.log(f"Executing {name} strategy on {pair}")
        self._loop = LoopingCall(func, self.client, self.account_id, pair, self.log)
        self._loop.start(10.0, now=True)

    def stop(self) -> None:
        if self._loop and self._loop.running:
            self._loop.stop()
            self.log("Strategy stopped")
            self._loop = None
