# trading_simulation/simulation_runner.py

#######################################
# IMPORTS
#######################################
import logging
import sys
from typing import List

# TinyTroupe / project imports
from tinytroupe.agent.tiny_person import TinyPerson

# Local module imports
from trading_simulation.trading_world import TradingWorld, run_trading_simulation
from trading_simulation.trading_agents import create_trader_persona

#######################################
# CLASSES
#######################################
class SimulationRunner:
    """
    A high-level orchestrator that sets up the trading simulation by:
      1. Creating or loading trader personas.
      2. Instantiating the TradingWorld environment.
      3. Running the simulation for a specified number of steps.
    """
    def __init__(self):
        """
        Constructor for the SimulationRunner.
        You can configure logging, read config files, etc. here if needed.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        self.logger.debug("SimulationRunner initialized.")

    def setup_traders(self) -> List[TinyPerson]:
        """
        Create or load trading personas. This is where you define your trader agents.
        For demonstration, we create a few with different risk tolerances.
        
        :return: A list of TinyPerson (trader personas).
        """
        trader1 = create_trader_persona(name="AliceTrader", trading_style="conservative", risk_tolerance=0.2)
        trader2 = create_trader_persona(name="BobTrader", trading_style="balanced", risk_tolerance=0.5)
        trader3 = create_trader_persona(name="EveTrader", trading_style="aggressive", risk_tolerance=0.8)
        self.logger.info("Created three trader personas with varying risk tolerances.")
        return [trader1, trader2, trader3]

    def setup_trading_world(self, agents: List[TinyPerson]) -> TradingWorld:
        """
        Initialize a TradingWorld environment with the given agents.
        
        :param agents: A list of trader personas.
        :return: An instance of TradingWorld.
        """
        # Example: we define some tickers. You can choose others or pass them as a parameter.
        ticker_list = ["AAPL", "MSFT", "AMZN", "TSLA", "GOOGL"]
        # We set some arguments as an example
        trading_world = TradingWorld(
            name="Stock Market Simulation",
            agents=agents,
            ticker_list=ticker_list,
            initial_capital=1e5,
            technical_indicators=None,
            use_news=True,
            news_update_interval=30,
            max_steps=200  # a demonstration
        )
        self.logger.info(f"TradingWorld created with tickers: {ticker_list}")
        return trading_world

    def run(self, total_steps: int = 50) -> None:
        """
        Run the full simulation, from building agents to running the environment.
        
        :param total_steps: How many steps the simulation should run.
        """
        self.logger.info("Setting up trader personas...")
        agents = self.setup_traders()

        self.logger.info("Creating TradingWorld environment...")
        world = self.setup_trading_world(agents)

        self.logger.info("Running trading simulation...")
        run_trading_simulation(world, total_steps=total_steps)
        self.logger.info("Simulation run complete.")

#######################################
# FUNCTIONS OUTSIDE OF CLASSES
#######################################
def main():
    """
    Main entry point for the simulation runner. Instantiates SimulationRunner
    and executes the simulation with default parameters.
    """
    runner = SimulationRunner()
    runner.run(total_steps=100)  # for example, run 100 steps

if __name__ == "__main__":
    main()