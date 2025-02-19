# trading_simulation/trading_world.py

#######################################
# IMPORTS
#######################################
import os
import time
import logging
import random
from typing import Any, Dict, List, Optional

# TinyTroupe imports
from tinytroupe.environment import TinyWorld
from tinytroupe.agent.tiny_person import TinyPerson
from tinytroupe.utils.config import get_config

# FinRL imports (example references)
# Note: Ensure FinRL is installed or included in your PYTHONPATH
from finrl.config import INDICATORS
from finrl.meta.env_stock_trading.env_stocktrading_np import StockTradingEnv
from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from finrl.meta.preprocessor.preprocessors import data_split
from finrl.config import (
    TRAIN_START_DATE,
    TRAIN_END_DATE,
    TRADE_START_DATE,
    TRADE_END_DATE
)

# If you have a DRLAgent or similar from FinRL, import it:
# from finrl.meta.agent.agent_ddpg import DRLAgent  # as an example

# News scraper imports
# We'll assume you have a module "news_scraper.scraper" that provides a function get_latest_news
# from news_scraper.scraper import get_latest_news

#######################################
# CLASSES
#######################################
class TradingWorld(TinyWorld):
    """
    A specialized TinyWorld that integrates a FinRL environment for stock trading
    and optionally pulls in external market news from a web scraper.
    
    Each step can update the market state based on the RL environment's simulation
    and can incorporate relevant news items. The multiagent framework from TinyTroupe
    can be used to represent trader personas reacting to these changes.
    """
    
    def __init__(
        self,
        name: str,
        agents: List[TinyPerson],
        ticker_list: Optional[List[str]] = None,
        initial_capital: float = 1e5,
        technical_indicators: Optional[List[str]] = None,
        use_news: bool = True,
        news_update_interval: int = 60,
        **kwargs
    ):
        """
        Constructor for the TradingWorld.
        
        :param name: A string name for this environment (e.g., "Stock Market Simulation").
        :param agents: A list of TinyPerson trader personas to place in the environment.
        :param ticker_list: A list of stock tickers to be used in the FinRL environment.
        :param initial_capital: The starting capital for each agent or the environment.
        :param technical_indicators: A list of technical indicators for the FinRL environment.
        :param use_news: If True, we fetch news from an external scraper to influence the environment.
        :param news_update_interval: The frequency (in seconds) at which we fetch new news articles.
        :param kwargs: Additional arguments to pass to the parent or for extended usage.
        """
        super().__init__(name, agents)
        self.logger = logging.getLogger(__name__)
        
        # FinRL environment setup
        self.ticker_list = ticker_list if ticker_list else ["AAPL", "MSFT", "AMZN"]
        self.initial_capital = initial_capital
        self.tech_indicators = technical_indicators if technical_indicators else INDICATORS
        
        # Prepare data for FinRL environment
        self.stock_env = self._init_finrl_env()
        
        # News scraping usage
        self.use_news = use_news
        self.news_update_interval = news_update_interval
        self.last_news_fetch_time = time.time()
        self.current_news: List[Dict[str, Any]] = []
        
        # Additional environment state
        self.market_time_step = 0
        self._max_steps = kwargs.get("max_steps", 1000)  # an example param
        self.logger.info(f"TradingWorld '{self.name}' created with tickers: {self.ticker_list}")
    
    def step(self, steps: int = 1) -> None:
        """
        Advance the simulation by a certain number of steps. Each step will:
        1. Optionally fetch new news (if time has elapsed).
        2. Step the FinRL environment to update market data.
        3. Provide updated info to the TinyTroupe agents, letting them act or react.
        4. Log any relevant events or decisions.
        
        :param steps: The number of steps to move forward.
        """
        for _ in range(steps):
            if self.market_time_step >= self._max_steps:
                self.logger.info("Reached max steps. No further stepping possible.")
                return
            
            # 1. Fetch news if needed
            if self.use_news:
                self._check_and_fetch_news()
            
            # 2. Step the FinRL environment
            obs, rewards, dones, info = self.stock_env.step([random.randint(0, 2)])  # e.g. random action for demonstration
            # In a real scenario, you'd retrieve actions from DRL or from the agent.
            
            # 3. Create a custom 'market update' stimulus for the agents
            market_stimulus = {
                "type": "MARKET_UPDATE",
                "observation": obs,
                "reward": rewards,
                "done": dones,
                "info": info,
                "news": self.current_news
            }
            
            # Let each agent handle the stimulus
            for agent in self.agents:
                agent.listen_and_act(market_stimulus)
            
            # Log the event
            self.logger.debug(f"Step {self.market_time_step}: Observations: {obs}, Rewards: {rewards}, Dones: {dones}")
            self.market_time_step += 1

    def reset(self) -> None:
        """
        Reset the environment, including the FinRL environment and any relevant local state.
        """
        self.logger.info("Resetting TradingWorld environment.")
        self.market_time_step = 0
        self.current_news = []
        self.stock_env.reset()
        for agent in self.agents:
            agent.reset_memory()
        self.logger.info("TradingWorld environment has been reset.")

    ###################################
    # Helper methods
    ###################################
    def _init_finrl_env(self) -> StockTradingEnv:
        """
        Initialize a FinRL StockTradingEnv using local or remote data. 
        This function downloads data from Yahoo as an example.
        """
        self.logger.info("Initializing FinRL environment with Yahoo data.")
        
        # 1. Download data
        df = YahooDownloader(
            start_date=TRAIN_START_DATE,
            end_date=TRADE_END_DATE,
            ticker_list=self.ticker_list
        ).fetch_data()
        
        # 2. Feature engineering
        fe = FeatureEngineer(
            use_technical_indicator=True,
            tech_indicator_list=self.tech_indicators,
            use_turbulence=True,
            user_defined_feature=False
        )
        processed_df = fe.preprocess_data(df)
        
        # 3. Split into training and trading for demonstration
        train_data = data_split(processed_df, TRAIN_START_DATE, TRAIN_END_DATE)
        trade_data = data_split(processed_df, TRADE_START_DATE, TRADE_END_DATE)
        
        # 4. Create environment (just for the trading phase)
        env_config = {
            "df": trade_data,
            "stock_dim": len(self.ticker_list),
            "hmax": 100,  # maximum number of shares to buy/sell
            "initial_amount": self.initial_capital,
            "transaction_cost_pct": 0.001,
            "tech_indicator_list": self.tech_indicators,
            "risk_indicator_col": "turbulence",
            "reward_scaling": 1e-4
        }
        env = StockTradingEnv(config=env_config)
        
        self.logger.info("FinRL environment initialization complete.")
        return env

    def _check_and_fetch_news(self) -> None:
        """
        Periodically fetch new market news using the external scraper if the interval has passed.
        """
        current_time = time.time()
        if (current_time - self.last_news_fetch_time) >= self.news_update_interval:
            self.logger.info("Fetching latest news from the web scraper...")
            try:
                # Example usage: self.current_news = get_latest_news(keywords=["stocks","market"])
                self.current_news = [
                    {
                        "headline": "Placeholder: Market sees unexpected rally",
                        "sentiment": "positive",
                        "timestamp": time.time()
                    },
                    {
                        "headline": "Placeholder: Tech stocks slump amid regulation fears",
                        "sentiment": "negative",
                        "timestamp": time.time()
                    }
                ]
            except Exception as e:
                self.logger.error(f"Error fetching news: {e}")
                self.current_news = []
            self.last_news_fetch_time = current_time

#######################################
# FUNCTIONS OUTSIDE OF CLASSES
#######################################

def run_trading_simulation(
    world: TradingWorld,
    total_steps: int = 100,
    step_batch: int = 1
) -> None:
    """
    Execute a full simulation run in the given TradingWorld environment.
    
    :param world: An instance of TradingWorld or subclass.
    :param total_steps: The total number of steps to simulate.
    :param step_batch: Number of steps to advance per iteration in the loop.
    """
    logging.info(f"Starting trading simulation for {total_steps} steps.")
    world.reset()
    
    while world.market_time_step < total_steps:
        world.step(step_batch)
        # Add a short sleep or additional logic if needed
        time.sleep(0.1)
    
    logging.info("Trading simulation completed.")