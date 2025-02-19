# trading_simulation/trading_agents.py

#######################################
# IMPORTS
#######################################
import logging
from typing import Any, Dict, List, Optional

# TinyTroupe imports
from tinytroupe.agent.tiny_person import TinyPerson

# If you have other relevant TinyTroupe modules for memory, environment, etc., import them as needed:
# from tinytroupe.environment import TinyWorld
# from tinytroupe.utils.config import get_config

#######################################
# CLASSES
#######################################
class TradingPersona(TinyPerson):
    """
    A specialized persona representing a trader in the integrated simulation.
    Inherits from TinyPerson but includes trading-specific attributes and logic.
    """

    def __init__(
        self,
        name: str,
        trading_style: str = "conservative",
        risk_tolerance: float = 0.2,
        *args,
        **kwargs
    ):
        """
        Constructor for a trading persona.
        
        :param name: The name of this trading persona (e.g., "AliceTrader").
        :param trading_style: A string representing the trading style (e.g., "conservative", "aggressive", etc.).
        :param risk_tolerance: A numeric representation of how risk-averse or risk-seeking this trader is.
        :param args: Additional positional args passed to TinyPerson.
        :param kwargs: Additional keyword args passed to TinyPerson.
        """
        super().__init__(name, *args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.trading_style = trading_style
        self.risk_tolerance = risk_tolerance

        # Example placeholders for portfolio or account state
        self.portfolio: Dict[str, int] = {}  # ticker -> shares
        self.cash_available: float = 100000.0

        # Memory or additional fields can be defined here if needed
        self.define("occupation", {
            "title": "Stock Trader",
            "description": f"Focuses on {trading_style} strategies with risk tolerance {risk_tolerance}"
        })

    def listen_and_act(self, stimulus: Any) -> None:
        """
        Overridden method that listens to environment stimuli and decides on a trading action.
        For example, it can read the 'MARKET_UPDATE' from the environment and place buy/sell orders.
        
        :param stimulus: The input from the environment (market updates, news, etc.).
        """
        super().listen(stimulus)  # Optionally store or process the stimulus

        if isinstance(stimulus, dict):
            stimulus_type = stimulus.get("type", "")
            if stimulus_type == "MARKET_UPDATE":
                self._handle_market_update(stimulus)
            else:
                # If it's some other type, do something else or do nothing
                pass

    #######################################
    # Internal Methods
    #######################################
    def _handle_market_update(self, market_stimulus: Dict[str, Any]) -> None:
        """
        React to a market update. This is a placeholder logic that can be replaced
        with real RL-based or rule-based trading decisions.
        
        :param market_stimulus: A dictionary containing info about the new market observation,
                                rewards, news, etc.
        """
        # Example placeholders
        observation = market_stimulus.get("observation", None)
        rewards = market_stimulus.get("reward", [0])
        done_flags = market_stimulus.get("done", [False])
        news_items = market_stimulus.get("news", [])

        # Decide on an action. For now, just log the info and do nothing.
        self.logger.debug(f"{self.name} sees market observation: {observation}")
        self.logger.debug(f"{self.name} sees reward: {rewards}, done: {done_flags}")
        if news_items:
            self.logger.debug(f"{self.name} sees news items: {news_items}")

        # If you had an RL agent or a rule-based system, you'd call it here
        # e.g. action = self.my_drl_agent.decide(observation)

        # For demonstration, let's do a placeholder buy or sell logic
        self._random_trading_decision()

    def _random_trading_decision(self) -> None:
        """
        Placeholder function to mimic a random buy or sell action.
        In a real scenario, you'd have logic that uses risk_tolerance,
        the current market data, etc.
        """
        import random
        # For demonstration, 1/10 chance to buy, 1/10 chance to sell, else hold
        decision_roll = random.random()
        if decision_roll < 0.1:
            self._buy_random_stock()
        elif decision_roll < 0.2:
            self._sell_random_stock()
        else:
            self.logger.debug(f"{self.name} decides to hold (no trade).")

    def _buy_random_stock(self) -> None:
        """
        Buys a small number of shares of a random stock (placeholder).
        """
        example_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]
        ticker = random.choice(example_tickers)
        shares_to_buy = 1

        # Placeholder logic: check if we have enough cash
        # In a real scenario, you'd factor in the price from the environment, transaction cost, etc.
        if self.cash_available > 100:  # pretend each share costs < 100
            self.cash_available -= 100
            self.portfolio[ticker] = self.portfolio.get(ticker, 0) + shares_to_buy
            self.logger.info(f"{self.name} buys {shares_to_buy} shares of {ticker}. Cash left: {self.cash_available}")
        else:
            self.logger.debug(f"{self.name} wants to buy {ticker} but has insufficient cash.")

    def _sell_random_stock(self) -> None:
        """
        Sells a small number of shares of a random stock (placeholder).
        """
        if not self.portfolio:
            self.logger.debug(f"{self.name} has no stocks to sell.")
            return
        ticker, shares_owned = random.choice(list(self.portfolio.items()))
        if shares_owned > 0:
            shares_to_sell = 1
            self.portfolio[ticker] -= shares_to_sell
            self.cash_available += 100  # placeholder for share price
            self.logger.info(f"{self.name} sells {shares_to_sell} shares of {ticker}. Cash now: {self.cash_available}")
            if self.portfolio[ticker] <= 0:
                del self.portfolio[ticker]
        else:
            self.logger.debug(f"{self.name} has zero shares of {ticker}, cannot sell.")

#######################################
# FUNCTIONS OUTSIDE OF CLASSES
#######################################
def create_trader_persona(
    name: str,
    trading_style: str,
    risk_tolerance: float
) -> TradingPersona:
    """
    Helper function to instantiate a TradingPersona with a specified name,
    trading style, and risk tolerance.
    
    :param name: The persona's name.
    :param trading_style: e.g., "conservative", "balanced", "aggressive".
    :param risk_tolerance: float representing how risk-hungry or risk-averse the persona is.
    :return: A new TradingPersona instance.
    """
    persona = TradingPersona(name=name, trading_style=trading_style, risk_tolerance=risk_tolerance)
    # Optionally define more attributes or set memory
    persona.define("preferences", {
        "interests": ["stock market", "economics", "financial news"]
    })
    persona.define("personality", {
        "traits": [
            f"Enjoys {trading_style} trading style with risk tolerance {risk_tolerance}",
            "Attentive to global economic indicators and financial press"
        ]
    })
    return persona