# Crypto Trading Bot

This Python script automates the process of buying and selling Dogecoin (DOGE) using the Robinhood Crypto Trading API. The bot monitors the price of DOGE, and based on specific conditions, it will execute trades to buy and sell DOGE, aiming to generate profit.

## Features

- **Monitors Dogecoin Price:** The bot continuously monitors the DOGE price using Robinhood's API.
- **Automated Trading:** Automatically buys DOGE when the price drops by 0.05% or more and sells when the price increases by 0.5% or more from the buy price.
- **Profit Protection:** Ensures that it only sells when the price is at least 0.5% higher than the purchase price to avoid losses.
- **Cooldown Period:** Waits for 5 minutes before resetting the initial buy price if no trade occurs.

## Prerequisites

- Python 3.8 or higher
- Robinhood API credentials (API Key and Private Key)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/crypto-trading-bot.git
   cd crypto-trading-bot

##

-Use at your own risk. This trades real world money.
-Was created with help form LLM.
