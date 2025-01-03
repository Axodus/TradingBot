from hummingbot.client.config.config_var import ConfigVar

def market_prompt() -> str:
    connector = whiterabbit_config_map.get("connector").value
    return f"Enter the token trading pair on {connector} >>> "

whiterabbit_config_map = {
    "strategy": ConfigVar(key="strategy", prompt="", default="white_rabbit"),
    "connector": ConfigVar(key="connector", prompt="Enter the name of the exchange >>> ", prompt_on_new=True),
    "market": ConfigVar(key="market", prompt=market_prompt, prompt_on_new=True),
    "rsi_period": ConfigVar(key="rsi_period", prompt="Enter RSI period >>> ", default=14),
    "rsi_long_level": ConfigVar(key="rsi_long_level", prompt="Enter RSI long level >>> ", default=30),
    "rsi_short_level": ConfigVar(key="rsi_short_level", prompt="Enter RSI short level >>> ", default=70),
    "volume_ma_period": ConfigVar(key="volume_ma_period", prompt="Enter volume MA period >>> ", default=21),
    "candlestick_patterns": ConfigVar(
        key="candlestick_patterns",
        prompt="Enter candlestick patterns to monitor (comma-separated, e.g., engulfing, hammer) >>> ",
        default="engulfing,hammer",
    ),
    "candlestick_source": ConfigVar(
        key="candlestick_source",
        prompt="Enter candlestick patterns library to use (options: ta-lib, pandas-ta) >>> ",
        default="pandas-ta"
    ),
}
