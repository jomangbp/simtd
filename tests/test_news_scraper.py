import pytest
from unittest.mock import patch, MagicMock
from news_scraper.scraper import NewsScraper

@pytest.fixture
def news_scraper():
    """Create a news scraper instance for testing."""
    return NewsScraper()

@pytest.fixture
def sample_news_data():
    """Sample news data for testing."""
    return [
        {
            'title': 'Test News 1',
            'content': 'Test content 1',
            'date': '2023-01-01',
            'source': 'Test Source'
        },
        {
            'title': 'Test News 2',
            'content': 'Test content 2',
            'date': '2023-01-02',
            'source': 'Test Source'
        }
    ]

def test_scraper_initialization(news_scraper):
    """Test if NewsScraper is properly initialized."""
    assert isinstance(news_scraper, NewsScraper)

@patch('news_scraper.scraper.requests.get')
def test_fetch_news(mock_get, news_scraper, sample_news_data):
    """Test news fetching functionality."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {'articles': sample_news_data}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    news = news_scraper.fetch_news('AAPL')
    
    assert len(news) == 2
    assert news[0]['title'] == 'Test News 1'
    assert news[1]['date'] == '2023-01-02'

@patch('news_scraper.scraper.requests.get')
def test_fetch_news_error_handling(mock_get, news_scraper):
    """Test error handling in news fetching."""
    # Mock a failed API response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        news_scraper.fetch_news('INVALID')

def test_process_news(news_scraper, sample_news_data):
    """Test news processing functionality."""
    processed_news = news_scraper.process_news(sample_news_data)
    
    assert isinstance(processed_news, list)
    assert len(processed_news) == 2
    assert all('sentiment' in news for news in processed_news)

def test_filter_news(news_scraper, sample_news_data):
    """Test news filtering functionality."""
    filtered_news = news_scraper.filter_news(
        sample_news_data,
        start_date='2023-01-01',
        end_date='2023-01-02'
    )
    
    assert len(filtered_news) == 2
    assert all(news['date'] >= '2023-01-01' for news in filtered_news)
    assert all(news['date'] <= '2023-01-02' for news in filtered_news)