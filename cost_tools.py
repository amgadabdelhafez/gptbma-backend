import yfinance as yf
from datetime import datetime, timedelta
    
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

import requests

# Define custom functions to interact with your API
def get_rate_card():
    response = requests.get('http://localhost:5000/rate_card')
    return response.json()

def get_billing_data(app_name: str):
    response = requests.get(f'http://localhost:5000/billing_data?app_name={app_name}')
    return response.json()

def calculate_cost(usage_data: dict):
    response = requests.post('http://localhost:5000/calculate_cost', json={'usage_data': usage_data})
    return response.json()


# Define input models for your tools
class BillingDataInput(BaseModel):
    app_name: str = Field(description="Name of the app")

# Create custom tools
class RateCardTool(BaseTool):
    name = "get_rate_card"
    description = "Retrieve rate card entries."
    
    def _run(self):
        return get_rate_card()

    def _arun(self):
        raise NotImplementedError("get_rate_card does not support async")

class BillingDataTool(BaseTool):
    name = "get_billing_data"
    description = "Retrieve billing data for a specific app."
    args_schema: type[BaseModel] = BillingDataInput
    
    def _run(self, app_name: str):
        return get_billing_data(app_name)

    def _arun(self, app_name: str):
        raise NotImplementedError("get_billing_data does not support async")


# Define input model for your tool
class CalculateCostInput(BaseModel):
    usage_data: dict = Field(description="""Usage data for cost calculation 
                             {
                                "usage_data": {
                                    "compute_cpu": 10,
                                    "compute_memory": 20,
                                    "observability_logs": 30
                                }
                            }""")

# Create a custom tool
class CalculateCostTool(BaseTool):
    name = "calculate_cost"
    description = "Calculate the effective cost based on usage data."
    args_schema: type[BaseModel] = CalculateCostInput
    
    def _run(self, usage_data: dict):
        return calculate_cost(usage_data)

    def _arun(self, usage_data: dict):
        raise NotImplementedError("calculate_cost does not support async")

def get_current_stock_price(ticker):
    """Method to get current stock price"""

    ticker_data = yf.Ticker(ticker)
    recent = ticker_data.history(period="1d")
    return {"price": recent.iloc[0]["Close"], "currency": ticker_data.info["currency"]}


def get_stock_performance(ticker, days):
    """Method to get stock price change in percentage"""

    past_date = datetime.today() - timedelta(days=days)
    ticker_data = yf.Ticker(ticker)
    history = ticker_data.history(start=past_date)
    old_price = history.iloc[0]["Close"]
    current_price = history.iloc[-1]["Close"]
    return {"percent_change": ((current_price - old_price) / old_price) * 100}


class CurrentStockPriceInput(BaseModel):
    """Inputs for get_current_stock_price"""

    ticker: str = Field(description="Ticker symbol of the stock")


class CurrentStockPriceTool(BaseTool):
    name = "get_current_stock_price"
    description = """
        Useful when you want to get current stock price.
        You should enter the stock ticker symbol recognized by the yahoo finance
        """
    args_schema: Type[BaseModel] = CurrentStockPriceInput

    def _run(self, ticker: str):
        price_response = get_current_stock_price(ticker)
        return price_response

    def _arun(self, ticker: str):
        raise NotImplementedError("get_current_stock_price does not support async")


class StockPercentChangeInput(BaseModel):
    """Inputs for get_stock_performance"""

    ticker: str = Field(description="Ticker symbol of the stock")
    days: int = Field(description="Timedelta days to get past date from current date")


class StockPerformanceTool(BaseTool):
    name = "get_stock_performance"
    description = """
        Useful when you want to check performance of the stock.
        You should enter the stock ticker symbol recognized by the yahoo finance.
        You should enter days as number of days from today from which performance needs to be check.
        output will be the change in the stock price represented as a percentage.
        """
    args_schema: Type[BaseModel] = StockPercentChangeInput

    def _run(self, ticker: str, days: int):
        response = get_stock_performance(ticker, days)
        return response

    def _arun(self, ticker: str):
        raise NotImplementedError("get_stock_performance does not support async")

llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0)

tools = [CurrentStockPriceTool(), StockPerformanceTool()]

agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

print()