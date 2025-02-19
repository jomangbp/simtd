import pytest
import pandas as pd
from unittest.mock import MagicMock
from trading_simulation.simulation_runner import SimulationRunner
from trading_simulation.trading_agents import TraderAgent, TraderPersona

@pytest.fixture
def simulation_runner():
    """Create a simulation runner instance for testing."""
    return SimulationRunner(
        initial_capital=100000.0,
        trading_days=10,
        tech_indicators=['macd', 'rsi']
    )

@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return pd.DataFrame({
        'open': [100, 101, 102],
        'high': [105, 106, 107],
        'low': [98, 99, 100],
        'close': [103, 104, 105],
        'volume': [1000, 1100, 1200]
    })

@pytest.fixture
def mock_trader_agent():
    """Create a mock trader agent for testing."""
    agent = TraderAgent(TraderPersona())
    agent.decide_action = MagicMock(return_value={'action': 1})
    return agent

def test_simulation_runner_initialization(simulation_runner):
    """Test if SimulationRunner is properly initialized."""
    assert simulation_runner.current_step == 0
    assert len(simulation_runner.agents) == 0
    assert isinstance(simulation_runner.simulation_history, list)

def test_add_agent(simulation_runner, mock_trader_agent):
    """Test adding an agent to the simulation."""
    simulation_runner.add_agent(mock_trader_agent)
    assert len(simulation_runner.agents) == 1
    assert simulation_runner.agents[0] == mock_trader_agent

def test_initialize_simulation(simulation_runner, sample_market_data):
    """Test simulation initialization with market data."""
    simulation_runner.initialize_simulation(sample_market_data)
    assert simulation_runner.current_step == 0
    assert len(simulation_runner.simulation_history) == 0

def test_simulation_step(simulation_runner, sample_market_data, mock_trader_agent):
    """Test single simulation step execution."""
    simulation_runner.add_agent(mock_trader_agent)
    simulation_runner.initialize_simulation(sample_market_data)
    
    step_result = simulation_runner.step()
    
    assert isinstance(step_result, dict)
    assert 'step' in step_result
    assert 'state' in step_result
    assert 'rewards' in step_result
    assert 'actions' in step_result
    assert simulation_runner.current_step == 1

def test_run_simulation(simulation_runner, sample_market_data, mock_trader_agent):
    """Test complete simulation run."""
    simulation_runner.add_agent(mock_trader_agent)
    simulation_runner.initialize_simulation(sample_market_data)
    
    history = simulation_runner.run_simulation()
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert all(isinstance(state, dict) for state in history)

def test_reset_simulation(simulation_runner, sample_market_data, mock_trader_agent):
    """Test simulation reset functionality."""
    simulation_runner.add_agent(mock_trader_agent)
    simulation_runner.initialize_simulation(sample_market_data)
    simulation_runner.step()
    
    simulation_runner.reset()
    assert simulation_runner.current_step == 0
    assert len(simulation_runner.simulation_history) == 0

def test_get_simulation_history(simulation_runner, sample_market_data, mock_trader_agent):
    """Test retrieving simulation history."""
    simulation_runner.add_agent(mock_trader_agent)
    simulation_runner.initialize_simulation(sample_market_data)
    simulation_runner.step()
    
    history = simulation_runner.get_simulation_history()
    assert isinstance(history, list)
    assert len(history) == 1
    assert isinstance(history[0], dict)