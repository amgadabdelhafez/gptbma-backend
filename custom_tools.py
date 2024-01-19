import requests
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# Define custom functions to interact with your API
def get_rate_card():
    response = requests.get('http://localhost/rate_card')
    return response.json()

def get_billing_data(app_name: str):
    response = requests.get(f'http://localhost/billing_data?app_name={app_name}')
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

# Define a custom function to interact with the /calculate_cost endpoint
def calculate_cost(usage_data: dict):
    response = requests.post('http://localhost/calculate_cost', json={'usage_data': usage_data})
    return response.json()

# Define input model for your tool
class CalculateCostInput(BaseModel):
    usage_data: dict = Field(description="Usage data for cost calculation")

# Create a custom tool
class CalculateCostTool(BaseTool):
    name = "calculate_cost"
    description = "Calculate the effective cost based on usage data."
    args_schema: type[BaseModel] = CalculateCostInput
    
    def _run(self, usage_data: dict):
        return calculate_cost(usage_data)

    def _arun(self, usage_data: dict):
        raise NotImplementedError("calculate_cost does not support async")
