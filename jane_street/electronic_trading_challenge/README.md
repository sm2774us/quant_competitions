# Jane Street Electronic Trading Challenge (ETC)

## Challenge Overview
The Jane Street Electronic Trading Challenge is a high-frequency trading simulation where participants build automated trading bots to compete in a simulated market. The goal is to maximize Profit and Loss (PnL) by executing various trading strategies while managing risk and adhering to exchange-imposed limits.

## Exchange Protocol
The bot communicates with the exchange over a TCP socket using a line-delimited JSON protocol.

### Message Types
- **Client to Exchange:**
  - `hello`: Initial handshake to register the team.
  - `add`: Place a new limit order.
  - `cancel`: Cancel an existing order.
  - `convert`: Request conversion between ETFs/ADRs and their underlying components.
- **Exchange to Client:**
  - `hello`: Confirmation of successful handshake and initial market state.
  - `book`: Update on the current order book for a symbol (bids and asks).
  - `trade`: Notification of a trade occurring in the market.
  - `fill`: Notification that the bot's order has been filled (partially or fully).
  - `out`: Notification that an order has been cancelled or closed.
  - `reject` / `error`: Feedback on invalid requests.

## Market Symbols & Dynamics
1. **BOND**: A stable asset typically priced at 1000.
2. **VALE & VALBZ**: VALBZ is the common stock, and VALE is its ADR (American Depositary Receipt). They are highly correlated and can be converted.
3. **XLF**: An ETF representing a basket of stocks.
   - **XLF Composition**: 10 units of XLF can be converted into/from:
     - 3 units of **BOND**
     - 2 units of **GS** (Goldman Sachs)
     - 3 units of **MS** (Morgan Stanley)
     - 2 units of **WFC** (Wells Fargo)

## Core Strategies

### 1. BOND Market Making
Since `BOND` is consistently priced at 1000, a simple market-making strategy involves placing buy orders at 999 and sell orders at 1001.

### 2. ADR Arbitrage (VALE/VALBZ)
Exploiting price discrepancies between the ADR (`VALE`) and the underlying stock (`VALBZ`).
- **Fair Value Estimation**: Use the price of the more liquid `VALBZ` to estimate the fair value of `VALE`.
- **Execution**: When `VALE` is undervalued relative to `VALBZ` (beyond the conversion fee), buy `VALE`, convert it to `VALBZ`, and sell `VALBZ`.

### 3. ETF Arbitrage (XLF)
Exploiting discrepancies between the ETF price and the Net Asset Value (NAV) of its components.
- **NAV Calculation**: $NAV = 3 \times Price(BOND) + 2 \times Price(GS) + 3 \times Price(MS) + 2 \times Price(WFC)$
- **Long ETF Arbitrage**: If $10 \times Price(XLF) < NAV - ConversionFee$, buy XLF, convert to components, and sell components.
- **Short ETF Arbitrage**: If $10 \times Price(XLF) > NAV + ConversionFee$, buy components, convert to XLF, and sell XLF.

## Technical Requirements
- Robust TCP connection management and reconnection logic.
- Efficient JSON parsing and state management.
- Low-latency order execution and position tracking.
- Risk management to avoid hitting position limits or executing loss-making trades.
