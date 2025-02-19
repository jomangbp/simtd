import pytest
import pandas as pd
from trading_simulation.trading_world import TradingWorld

@pytest.fixture
def trading_world():
    """Create a basic trading world instance for testing."""
    return TradingWorld(
        initial_capital=100000.0,
        trading_days=10,
        tech_indicator_list=['macd', 'rsi']
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

def test_trading_world_initialization(trading_world):
    """Test if TradingWorld is properly initialized with given parameters."""
    assert trading_world.initial_capital == 100000.0
    assert trading_world.trading_days == 10
    assert trading_world.tech_indicator_list == ['macd', 'rsi']
    assert trading_world.market_env is None
    assert trading_world.current_state == {}

def test_market_initialization(trading_world, sample_market_data):
    """Test if market environment is properly initialized with data."""
    trading_world.initialize_market(sample_market_data)
    assert trading_world.market_env is not None
    assert isinstance(trading_world.current_state, dict)

def test_step_without_initialization(trading_world):
    """Test if step raises error when market is not initialized."""
    with pytest.raises(RuntimeError, match="Market environment not initialized"):
        trading_world.step({'action': 1})

def test_step_execution(trading_world, sample_market_data):
    """Test if step execution returns correct format of results."""
    trading_world.initialize_market(sample_market_data)
    result = trading_world.step({'action': 1})
    
    assert isinstance(result, dict)
    assert 'state' in result
    assert 'rewards' in result
    assert 'done' in result
    assert 'info' in result

def test_get_state(trading_world, sample_market_data):
    """Test if get_state returns current state correctly."""
    trading_world.initialize_market(sample_market_data)
    state = trading_world.get_state()
    assert isinstance(state, dict)
    assert state == trading_world.current_state

def test_reset(trading_world, sample_market_data):
    """Test if reset returns environment to initial state."""
    trading_world.initialize_market(sample_market_data)
    initial_state = trading_world.current_state.copy()
    
    # Perform some actions
    trading_world.step({'action': 1})
    
    # Reset and verify
    reset_state = trading_world.reset()
    assert isinstance(reset_state, dict)
    assert trading_world.current_state != initial_state  # States should be different after reset