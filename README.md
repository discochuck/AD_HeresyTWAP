# AD_HeresyTWAP

Automated bot to purchase **0.25 AVAX** worth of **HERESY** tokens daily via Trader Joe (LFJ.gg) on Avalanche.

## Features

- **Daily TWAP Purchase**: Executes a time-weighted average price swap of 0.25 AVAX → HERESY every 24 hours.
- **Heroku-Ready**: One-click deploy to Heroku with scheduler integration.
- **Zero Slippage Tolerance**: Accepts any output to guarantee execution.
- **Simple Configuration**: Use environment variables for all secrets and addresses.

## Prerequisites

- **Git**
- **Python 3.8+**
- **Heroku CLI** (for deployment)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/wrathtank/AD_HeresyTWAP.git
   cd AD_HeresyTWAP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** at the project root:
   ```ini
   AVAX_RPC_URL=https://api.avax.network/ext/bc/C/rpc
   BOT_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
   WAVAX_ADDRESS=0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7
   HERESY_ADDRESS=0xd57741411cc5d9bf1786523e40412d77946a55aa 
   JOE_ROUTER=0x60ae616a2155ee3d9a68541ba4544862310933d4
   ```

4. **Deploy to Heroku**
   ```bash
   heroku create adheresytwap
   git push heroku main
   ```

5. **Configure environment variables on Heroku**
   ```bash
   heroku config:set AVAX_RPC_URL="https://api.avax.network/ext/bc/C/rpc" \
                     BOT_PRIVATE_KEY="0xYOUR_PRIVATE_KEY" \
                     WAVAX_ADDRESS="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7" \
                     HERESY_ADDRESS="0xd57741411cc5d9bf1786523e40412d77946a55aa" \
                     JOE_ROUTER="0x60ae616a2155ee3d9a68541ba4544862310933d4" \
                     --app adheresytwap
   ```

6. **Test the bot**
   ```bash
   heroku run python buy_heresy.py --app adheresytwap
   ```

7. **Schedule daily execution**
   - In the Heroku Dashboard, under **Resources**, add **Heroku Scheduler**.
   - Create a new job:
     - **Command**: `python buy_heresy.py`
     - **Frequency**: Daily
     - **Next due**: pick your preferred UTC time

## Usage

Once scheduled, the bot will run daily and print a log line:
```
🔄 Swap TX → https://snowtrace.io/tx/<txHash>
```
You can verify each transaction on SnowTrace.

## Contributing

Feel free to open issues or pull requests for improvements or bug fixes.

---

**Credit**: Developed by The City, LLC.

