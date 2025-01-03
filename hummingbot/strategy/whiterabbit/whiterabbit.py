from decimal import Decimal
import logging
from hummingbot.core.event.events import OrderType
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.logger import HummingbotLogger
from hummingbot.strategy.strategy_py_base import StrategyPyBase
import pandas_ta as pta
try:
    import talib  # TA-Lib
except ImportError:
    talib = None

wr_logger = None

class WhiteRabbit(StrategyPyBase):
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global wr_logger
        if wr_logger is None:
            wr_logger = logging.getLogger(__name__)
        return wr_logger

    def __init__(self, market_info: MarketTradingPairTuple, config):
        super().__init__()
        self._market_info = market_info
        self._config = config
        self._connector_ready = False
        self._order_completed = False
        self.add_markets([market_info.market])

    async def update_indicators(self):
        # Fetch candles data
        candles_df = self.market_data_provider.get_candles_df(
            connector_name=self._config.candles_connector,
            trading_pair=self._config.candles_trading_pair,
            interval=self._config.interval,
            max_records=200
        )

        # Add RSI
        candles_df["rsi"] = pta.rsi(candles_df["close"], length=self._config.rsi_period)

        # Add volume moving average
        candles_df["volume_ma"] = candles_df["volume"].rolling(window=self._config.volume_ma_period).mean()

        # Add candlestick patterns based on the selected library
        if self._config.candlestick_source.lower() == "ta-lib" and talib:
            for pattern in self._config.candlestick_patterns.split(","):
                func = getattr(talib, f"CDL{pattern.strip().upper()}", None)
                if func:
                    candles_df[f"pattern_{pattern.strip()}"] = func(
                        candles_df["open"],
                        candles_df["high"],
                        candles_df["low"],
                        candles_df["close"]
                    )
        elif self._config.candlestick_source.lower() == "pandas-ta":
            for pattern in self._config.candlestick_patterns.split(","):
                func = getattr(pta, f"cdl_{pattern.strip().lower()}", None)
                if func:
                    candles_df[f"pattern_{pattern.strip()}"] = func(candles_df)

        return candles_df

    async def tick(self, timestamp: float):
        if not self._connector_ready:
            self._connector_ready = self._market_info.market.ready
            if not self._connector_ready:
                self.logger().warning(f"{self._market_info.market.name} is not ready. Please wait...")
                return
            else:
                self.logger().info(f"{self._market_info.market.name} is ready. Trading started.")

        # Update indicators
        candles_df = await self.update_indicators()

        # Current signals
        current_signal = self._bollinger_controller.processed_data.get("signal", 0)
        current_rsi = candles_df["rsi"].iloc[-1]
        current_volume = candles_df["volume"].iloc[-1]
        volume_ma = candles_df["volume_ma"].iloc[-1]

        # Trade logic with RSI levels and Volume analysis
        if current_signal == 1 and current_rsi > self._config.rsi_long_level and current_volume <= volume_ma:
            # Long condition
            order_id = self.buy_with_specific_market(
                self._market_info,
                Decimal("0.005"),  # Amount
                OrderType.LIMIT,
                self._market_info.get_mid_price()
            )
            self.logger().info(f"Submitted long order {order_id}")

        elif current_signal == -1 and current_rsi < self._config.rsi_short_level and current_volume <= volume_ma:
            # Short condition
          
