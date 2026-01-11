import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
import aiohttp
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# You should get your API key from Alpha Vantage: https://www.alphavantage.co/
ALPHA_VANTAGE_API_KEY = "demo"  # Replace with your actual API key
BASE_URL = "https://www.alphavantage.co/query"

class MarketDataService:
    def __init__(self):
        self.stocks_cache = {}
        self.last_update = None
        self.update_interval = timedelta(minutes=5)
        self.stock_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", 
            "NVDA", "TSLA", "JPM", "V", "WMT"
        ]
        
    async def fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time stock data from Alpha Vantage API"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "Global Quote" in data:
                            quote = data["Global Quote"]
                            return {
                                "symbol": symbol,
                                "price": float(quote.get("05. price", 0)),
                                "change": float(quote.get("09. change", 0)),
                                "change_percent": float(quote.get("10. change percent", "0").strip("%")),
                                "volume": int(quote.get("06. volume", 0)),
                            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        # Return simulated data if API fails
        return self.get_simulated_stock_data(symbol)

    def get_simulated_stock_data(self, symbol: str) -> Dict:
        """Generate simulated stock data for testing"""
        base_prices = {
            "AAPL": 150.25,
            "MSFT": 310.75,
            "GOOGL": 2750.20,
            "AMZN": 3300.50,
            "META": 330.25,
            "NVDA": 420.75,
            "TSLA": 850.50,
            "JPM": 140.30,
            "V": 230.45,
            "WMT": 145.60
        }
        
        base_price = base_prices.get(symbol, 100.0)
        change_percent = random.uniform(-3.0, 3.0)
        change = base_price * (change_percent / 100)
        
        return {
            "symbol": symbol,
            "name": self.get_company_name(symbol),
            "price": base_price + change,
            "change": change_percent,
            "volume": random.randint(500000, 5000000),
            "chart_data": [
                base_price + random.uniform(-5, 5) 
                for _ in range(10)
            ]
        }

    def get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "TSLA": "Tesla Inc.",
            "JPM": "JPMorgan Chase & Co.",
            "V": "Visa Inc.",
            "WMT": "Walmart Inc."
        }
        return names.get(symbol, symbol)

    async def get_real_time_stock_data(self, symbol: str) -> Dict:
        """Get real-time data for a single stock"""
        try:
            logger.info(f"Fetching data for {symbol}")
            stock = yf.Ticker(symbol)
            
            # Get basic info
            info = stock.info
            if not info:
                logger.error(f"No info available for {symbol}")
                return None
                
            # Get historical data
            hist = stock.history(period="2d")
            if len(hist) < 2:
                logger.error(f"Insufficient historical data for {symbol}")
                return None
                
            current_price = info.get('regularMarketPrice', 0)
            if not current_price:
                current_price = hist['Close'].iloc[-1]
                
            previous_close = hist['Close'].iloc[-2]
            change = ((current_price - previous_close) / previous_close) * 100
            
            technical_indicators = self.calculate_technical_indicators(hist)
            
            data = {
                "symbol": symbol,
                "name": info.get('shortName', symbol),
                "price": current_price,
                "change": round(change, 2),
                "market_cap": info.get('marketCap', 0),
                "volume": info.get('volume', 0),
                "technical_indicators": technical_indicators,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully fetched data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
            
    def calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict:
        """Calculate technical indicators for a stock"""
        try:
            close_prices = hist['Close']
            
            # Calculate moving averages
            ma20 = close_prices.rolling(window=20).mean().iloc[-1]
            ma50 = close_prices.rolling(window=50).mean().iloc[-1]
            
            # Calculate RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            return {
                "ma20": round(float(ma20), 2) if not pd.isna(ma20) else 0,
                "ma50": round(float(ma50), 2) if not pd.isna(ma50) else 0,
                "rsi": round(float(rsi), 2) if not pd.isna(rsi) else 50
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {"ma20": 0, "ma50": 0, "rsi": 50}
            
    async def get_market_overview(self) -> Dict:
        """Get overall market statistics"""
        try:
            logger.info("Fetching market overview")
            sp500 = yf.Ticker("^GSPC")
            vix = yf.Ticker("^VIX")
            
            overview = {
                "total_volume": sp500.info.get("volume", 0),
                "market_cap": sp500.info.get("marketCap", 0),
                "active_stocks": 500,
                "volatility_index": vix.info.get("regularMarketPrice", 0)
            }
            
            logger.info("Successfully fetched market overview")
            return overview
            
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return {
                "total_volume": 0,
                "market_cap": 0,
                "active_stocks": 0,
                "volatility_index": 0
            }
            
    async def get_real_time_market_data(self) -> Dict:
        """Get comprehensive real-time market data"""
        try:
            logger.info("Starting to fetch market data")
            
            # Fetch market overview
            market_overview = await self.get_market_overview()
            
            # Fetch stock data concurrently
            tasks = [self.get_real_time_stock_data(symbol) for symbol in self.stock_symbols]
            stock_data = await asyncio.gather(*tasks)
            
            # Filter out None values and sort by market cap
            valid_stocks = [data for data in stock_data if data is not None]
            sorted_stocks = sorted(valid_stocks, key=lambda x: x['market_cap'], reverse=True)
            
            logger.info(f"Successfully fetched data for {len(valid_stocks)} stocks")
            
            return {
                "market_overview": market_overview,
                "top_stocks": sorted_stocks
            }
            
        except Exception as e:
            logger.error(f"Error in get_real_time_market_data: {str(e)}")
            return {
                "market_overview": {
                    "total_volume": 0,
                    "market_cap": 0,
                    "active_stocks": 0,
                    "volatility_index": 0
                },
                "top_stocks": []
            }

    async def get_market_data(self) -> Dict:
        """Get comprehensive market data including stocks and indices"""
        # Only update cache if enough time has passed
        if (not self.last_update or 
            datetime.now() - self.last_update > self.update_interval):
            
            # List of stock symbols to track
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", 
                      "NVDA", "TSLA", "JPM", "V", "WMT"]
            
            # Fetch all stock data concurrently
            tasks = [self.fetch_stock_data(symbol) for symbol in symbols]
            stock_data = await asyncio.gather(*tasks)
            
            # Calculate market summary
            advancing = sum(1 for stock in stock_data if stock["change"] > 0)
            total_volume = sum(stock["volume"] for stock in stock_data)
            
            self.stocks_cache = {
                "stocks": stock_data,
                "indices": [
                    {
                        "symbol": "^GSPC",
                        "name": "S&P 500",
                        "value": 4200.50 + random.uniform(-20, 20),
                        "change": random.uniform(-1, 1),
                        "chart_data": [4180 + random.uniform(-10, 10) for _ in range(10)]
                    }
                ],
                "market_summary": {
                    "total_volume": total_volume,
                    "advancing_stocks": advancing,
                    "declining_stocks": len(stock_data) - advancing,
                    "volatility_index": 15 + random.uniform(-2, 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.last_update = datetime.now()
        
        return self.stocks_cache

async def get_real_time_market_data() -> Dict:
    """
    Simulates real-time market data
    """
    # Simulate some delay as if fetching from external API
    await asyncio.sleep(0.1)
    
    # Generate mock market data
    current_time = datetime.now()
    
    market_indices = {
        'SP500': {
            'value': round(random.uniform(4000, 4500), 2),
            'change': round(random.uniform(-50, 50), 2),
        },
        'NASDAQ': {
            'value': round(random.uniform(14000, 15000), 2),
            'change': round(random.uniform(-100, 100), 2),
        },
        'DOW': {
            'value': round(random.uniform(33000, 34000), 2),
            'change': round(random.uniform(-200, 200), 2),
        }
    }
    
    # Add percentage changes
    for index in market_indices:
        market_indices[index]['percent_change'] = round(
            (market_indices[index]['change'] / market_indices[index]['value']) * 100, 2
        )
    
    # Generate some trending stocks
    trending_stocks = [
        {
            'symbol': 'AAPL',
            'price': round(random.uniform(170, 180), 2),
            'change': round(random.uniform(-5, 5), 2),
        },
        {
            'symbol': 'MSFT',
            'price': round(random.uniform(330, 340), 2),
            'change': round(random.uniform(-7, 7), 2),
        },
        {
            'symbol': 'GOOGL',
            'price': round(random.uniform(140, 150), 2),
            'change': round(random.uniform(-4, 4), 2),
        }
    ]
    
    # Add percentage changes for stocks
    for stock in trending_stocks:
        stock['percent_change'] = round((stock['change'] / stock['price']) * 100, 2)
    
    return {
        'timestamp': current_time.isoformat(),
        'market_indices': market_indices,
        'trending_stocks': trending_stocks,
        'status': 'success'
    }

market_service = MarketDataService()
