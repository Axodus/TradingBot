from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.strategy.whiterabbit import WhiteRabbit
from hummingbot.strategy.whiterabbit.whiterabbit_config_map import whiterabbit_config_map as c_map

def start(self):
    connector = c_map.get("connector").value.lower()
    market = c_map.get("market").value

    self._initialize_markets([(connector, [market])])
    base, quote = market.split("-")
    market_info = MarketTradingPairTuple(self.markets[connector], market, base, quote)
    self.market_trading_pair_tuples = [market_info]

    config = {
        "candles_connector": connector,
        "candles_trading_pair": market,
        "interval": c_map.get("interval").value,
        "rsi_period": c_map.get("rsi_period").value,
        "rsi_level": c_map.get("rsi_level").value,
        "volume_ma_period": c_map.get("volume_ma_period").value,
        "candlestick_patterns": c_map.get("candlestick_patterns").value,
    }
    self.strategy = WhiteRabbit(market_info, config)
