# data_fetcher.py
# Handles stock data retrieval and preprocessing for the LSTM model.
# Data fetching approach adapted from yfinance documentation:
# https://pypi.org/project/yfinance/
# Normalization approach adapted from:
# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html

import random
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# ── Ticker name mappings for display names ─────────────────
# 70+ stocks across US / A-Share / HK markets
_STOCK_NAMES = {
    # ── US Mega-Cap (Magnificent 7 +) ──
    "AAPL":  "Apple Inc.",         "MSFT":  "Microsoft Corp.",
    "NVDA":  "NVIDIA Corp.",       "GOOGL": "Alphabet Inc.",
    "AMZN":  "Amazon.com",         "META":  "Meta Platforms",
    "TSLA":  "Tesla Inc.",
    # ── US Tech / Semis ──
    "AVGO":  "Broadcom Inc.",      "AMD":   "AMD Inc.",
    "INTC":  "Intel Corp.",        "QCOM":  "Qualcomm Inc.",
    "TXN":   "Texas Instruments",  "MU":    "Micron Technology",
    "AMAT":  "Applied Materials",  "LRCX":  "Lam Research",
    "CRM":   "Salesforce Inc.",    "ADBE":  "Adobe Inc.",
    "ORCL":  "Oracle Corp.",       "CSCO":  "Cisco Systems",
    "PLTR":  "Palantir Tech.",     "SNOW":  "Snowflake Inc.",
    # ── US Finance ──
    "JPM":   "JPMorgan Chase",     "BAC":   "Bank of America",
    "GS":    "Goldman Sachs",      "MS":    "Morgan Stanley",
    "V":     "Visa Inc.",          "MA":    "Mastercard Inc.",
    "BRK-B": "Berkshire Hathaway",
    # ── US Consumer / Health / Other ──
    "WMT":   "Walmart Inc.",       "COST":  "Costco Wholesale",
    "NFLX":  "Netflix Inc.",       "DIS":   "Walt Disney",
    "PFE":   "Pfizer Inc.",        "JNJ":   "Johnson & Johnson",
    "XOM":   "Exxon Mobil",        "CVX":   "Chevron Corp.",
    "UBER":  "Uber Technologies",  "BA":    "Boeing Co.",
    # ── US Chinese ADRs ──
    "BABA":  "Alibaba Group",      "BIDU":  "Baidu Inc.",
    "NIO":   "NIO Inc.",           "PDD":   "PDD Holdings",
    # ── A-Share Shanghai (.SS) ──
    "600519.SS": "贵州茅台",        "601318.SS": "中国平安",
    "603259.SS": "药明康德",        "600036.SS": "招商银行",
    "601899.SS": "紫金矿业",        "600900.SS": "长江电力",
    "600276.SS": "恒瑞医药",        "600809.SS": "山西汾酒",
    "600030.SS": "中信证券",        "601398.SS": "工商银行",
    # ── A-Share Shenzhen (.SZ) ──
    "000858.SZ": "五粮液",          "300750.SZ": "宁德时代",
    "002594.SZ": "比亚迪",          "000725.SZ": "京东方A",
    "000333.SZ": "美的集团",        "002475.SZ": "立讯精密",
    "300308.SZ": "中际旭创",        "300502.SZ": "新易盛",
    "300059.SZ": "东方财富",        "002415.SZ": "海康威视",
    "000001.SZ": "平安银行",        "002230.SZ": "科大讯飞",
    "300274.SZ": "阳光电源",        "002371.SZ": "北方华创",
    "000568.SZ": "泸州老窖",        "300124.SZ": "汇川技术",
    # ── Hong Kong (.HK) ──
    "0700.HK": "腾讯控股",          "9988.HK": "阿里巴巴-W",
    "3690.HK": "美团-W",           "1810.HK": "小米集团-W",
    "9618.HK": "京东集团-SW",      "9999.HK": "网易-S",
    "1024.HK": "快手-W",           "2015.HK": "理想汽车-W",
    "1211.HK": "比亚迪股份",        "2318.HK": "中国平安-H",
    "0388.HK": "香港交易所",        "0005.HK": "汇丰控股",
    "0941.HK": "中国移动",          "1398.HK": "工商银行-H",
    "2269.HK": "药明生物",          "9863.HK": "零跑汽车",
    "9992.HK": "泡泡玛特",          "1876.HK": "百胜中国",
}

_STOCK_SECTORS = {
    # US
    "AAPL": "消费电子",  "MSFT": "软件",     "NVDA": "半导体",
    "GOOGL":"互联网",    "AMZN": "电商",      "META": "社交",
    "TSLA": "汽车",      "AVGO": "半导体",    "AMD": "半导体",
    "INTC": "半导体",    "QCOM": "通信",      "TXN": "半导体",
    "MU":   "存储",      "AMAT": "设备",      "LRCX": "设备",
    "CRM":  "软件",      "ADBE": "软件",      "ORCL": "软件",
    "CSCO": "通信",      "PLTR": "AI大数据",  "SNOW": "云计算",
    "JPM":  "银行",      "BAC":  "银行",      "GS": "投行",
    "MS":   "投行",      "V":    "支付",      "MA": "支付",
    "BRK-B":"保险",      "WMT":  "零售",      "COST":"零售",
    "NFLX": "流媒体",    "DIS":  "娱乐",      "PFE": "医药",
    "JNJ":  "医药",      "XOM":  "能源",      "CVX": "能源",
    "UBER": "出行",      "BA":   "航空",      "BABA":"电商",
    "BIDU": "AI搜索",    "NIO":  "新能源车",  "PDD": "电商",
    # A-Share Shanghai
    "600519.SS":"白酒",   "601318.SS":"保险",  "603259.SS":"医药",
    "600036.SS":"银行",   "601899.SS":"矿业",  "600900.SS":"电力",
    "600276.SS":"医药",   "600809.SS":"白酒",  "600030.SS":"券商",
    "601398.SS":"银行",
    # A-Share Shenzhen
    "000858.SZ":"白酒",   "300750.SZ":"电池",  "002594.SZ":"汽车",
    "000725.SZ":"面板",   "000333.SZ":"家电",  "002475.SZ":"电子",
    "300308.SZ":"光模块", "300502.SZ":"光模块","300059.SZ":"券商",
    "002415.SZ":"安防",   "000001.SZ":"银行",  "002230.SZ":"AI",
    "300274.SZ":"光伏",   "002371.SZ":"半导体","000568.SZ":"白酒",
    "300124.SZ":"工业",   # HK
    "0700.HK":"互联网",   "9988.HK":"电商",    "3690.HK":"本地生活",
    "1810.HK":"消费电子", "9618.HK":"电商",    "9999.HK":"游戏",
    "1024.HK":"短视频",   "2015.HK":"新能源车","1211.HK":"汽车",
    "2318.HK":"保险",     "0388.HK":"交易所",  "0005.HK":"银行",
    "0941.HK":"电信",     "1398.HK":"银行",    "2269.HK":"医药",
    "9863.HK":"汽车",     "9992.HK":"消费",    "1876.HK":"餐饮",
}

# ── Sector categories for heatmap / grouping ─────────────────
_SECTOR_GROUPS = {
    "🇺🇸 美股": {
        "科技七巨头": ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA"],
        "半导体":    ["AVGO","AMD","INTC","QCOM","TXN","MU","AMAT","LRCX"],
        "软件服务":  ["CRM","ADBE","ORCL","CSCO","PLTR","SNOW"],
        "金融":      ["JPM","BAC","GS","MS","V","MA","BRK-B"],
        "消费零售":  ["WMT","COST","NFLX","DIS","UBER"],
        "医疗健康":  ["PFE","JNJ"],
        "能源工业":  ["XOM","CVX","BA"],
        "中概股":    ["BABA","BIDU","NIO","PDD"],
    },
    "🇨🇳 A股": {
        "白酒消费":  ["600519.SS","000858.SZ","000568.SZ","600809.SS"],
        "新能源":    ["300750.SZ","002594.SZ","300274.SZ"],
        "半导体电子":["002371.SZ","002475.SZ","000725.SZ","300502.SZ","300308.SZ"],
        "金融":      ["601318.SS","600036.SS","601398.SS","600030.SS","300059.SZ","000001.SZ"],
        "医药":      ["603259.SS","600276.SS"],
        "电力工业":  ["600900.SS","601899.SS","300124.SZ","000333.SZ"],
        "AI科技":    ["002230.SZ","002415.SZ"],
    },
    "🇭🇰 港股": {
        "互联网":    ["0700.HK","9988.HK","3690.HK","9618.HK","9999.HK","1024.HK"],
        "硬件汽车":  ["1810.HK","2015.HK","1211.HK","9863.HK"],
        "金融":      ["2318.HK","0388.HK","0005.HK","1398.HK"],
        "电信医药消费":["0941.HK","2269.HK","9992.HK","1876.HK"],
    },
}

# ── Index definitions ────────────────────────────────────────
_INDICES = [
    {"ticker": "^GSPC",   "region": "美国", "name": "S&P 500"},
    {"ticker": "^IXIC",   "region": "美国", "name": "NASDAQ"},
    {"ticker": "^DJI",    "region": "美国", "name": "道琼斯"},
    {"ticker": "000001.SS","region": "中国", "name": "上证指数"},
    {"ticker": "399001.SZ","region": "中国", "name": "深证成指"},
    {"ticker": "399006.SZ","region": "中国", "name": "创业板指"},
    {"ticker": "^HSI",    "region": "香港", "name": "恒生指数"},
    {"ticker": "^N225",   "region": "日本", "name": "日经225"},
    {"ticker": "^FTSE",   "region": "欧洲", "name": "FTSE 100"},
]

# ── Market grouping ──────────────────────────────────────────
_MARKETS = {
    "us": [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA",
        "AVGO","AMD","INTC","QCOM","TXN","MU","AMAT","LRCX",
        "CRM","ADBE","ORCL","CSCO","PLTR","SNOW",
        "JPM","BAC","GS","MS","V","MA","BRK-B",
        "WMT","COST","NFLX","DIS","UBER",
        "PFE","JNJ","XOM","CVX","BA",
        "BABA","BIDU","NIO","PDD",
    ],
    "cn": [
        "600519.SS","000858.SZ","000568.SZ","600809.SS",
        "300750.SZ","002594.SZ","300274.SZ",
        "002371.SZ","002475.SZ","000725.SZ","300502.SZ","300308.SZ",
        "601318.SS","600036.SS","601398.SS","600030.SS","300059.SZ","000001.SZ",
        "603259.SS","600276.SS",
        "600900.SS","601899.SS","300124.SZ","000333.SZ",
        "002230.SZ","002415.SZ",
    ],
    "hk": [
        "0700.HK","9988.HK","3690.HK","9618.HK","9999.HK","1024.HK",
        "1810.HK","2015.HK","1211.HK","9863.HK",
        "2318.HK","0388.HK","0005.HK","1398.HK",
        "0941.HK","2269.HK","9992.HK","1876.HK",
    ],
}


def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical closing price data for a given stock ticker.

    Parameters:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        period (str): Historical period to fetch (default: 2 years).

    Returns:
        pd.DataFrame: DataFrame containing the 'Close' price column.

    Raises:
        ValueError: If the ticker is invalid or no data is returned.
    """
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)

    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Please check the symbol and try again.")

    # Keep only the closing price
    close_df = df[['Close']].copy()

    # Drop any rows with missing values
    close_df.dropna(inplace=True)

    if len(close_df) < 100:
        raise ValueError(f"Insufficient data for '{ticker}'. Only {len(close_df)} records found (minimum 100 required).")

    return close_df


def preprocess_data(df: pd.DataFrame, look_back: int = 60):
    """
    Normalize data and create sliding-window sequences for LSTM training.

    Parameters:
        df (pd.DataFrame): Raw closing price DataFrame.
        look_back (int): Number of past days used as input features.

    Returns:
        tuple: (X, y, scaler)
            X (np.ndarray): Input sequences of shape (samples, look_back, 1).
            y (np.ndarray): Target values of shape (samples, 1).
            scaler (MinMaxScaler): Fitted scaler for inverse transformation.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values)

    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    X = np.array(X)
    y = np.array(y)

    # Reshape X to (samples, timesteps, features) as required by LSTM
    X = X.reshape((X.shape[0], X.shape[1], 1))

    return X, y, scaler


def train_test_split_timeseries(X: np.ndarray, y: np.ndarray, split_ratio: float = 0.8):
    """
    Split data into training and testing sets while preserving time order.

    Parameters:
        X (np.ndarray): Input sequences.
        y (np.ndarray): Target values.
        split_ratio (float): Proportion of data for training (default: 80%).

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    split_index = int(len(X) * split_ratio)

    X_train = X[:split_index]
    X_test  = X[split_index:]
    y_train = y[:split_index]
    y_test  = y[split_index:]

    return X_train, X_test, y_train, y_test


# ── Real-time quote fetching ─────────────────────────────────

def fetch_realtime_quotes(tickers: list) -> dict:
    """
    Fetch current real-time quotes for a list of ticker symbols.

    Uses yfinance's fast_info for near-real-time data (may be delayed
    ~15 min for non-US markets). Falls back to latest close if real-time
    data is not available.

    Parameters:
        tickers (list): List of yfinance ticker symbols.

    Returns:
        dict: {ticker_symbol: {price, change, changePercent, name, sector}}
              Empty dict for any ticker whose data cannot be fetched.
    """
    if not tickers:
        return {}

    results = {}
    try:
        # Use batch Tickers object for efficient fetching
        ticker_str = " ".join(tickers)
        yt = yf.Tickers(ticker_str)

        for sym in tickers:
            try:
                tk = yt.tickers.get(sym)
                if tk is None:
                    continue

                # Try fast_info first for real-time data
                info = tk.fast_info
                price = getattr(info, "last_price", None) or getattr(info, "regular_market_previous_close", None)
                prev_close = getattr(info, "regular_market_previous_close", None) or getattr(info, "previous_close", None)

                if price is None or price <= 0:
                    # Fallback: get last close from 1-day history
                    hist = tk.history(period="2d")
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])
                        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price

                if price is None or price <= 0:
                    continue

                change_val = price - prev_close if prev_close else 0
                change_pct = (change_val / prev_close * 100) if prev_close and prev_close != 0 else 0

                name = _STOCK_NAMES.get(sym, sym)
                sector = _STOCK_SECTORS.get(sym, "综合")

                results[sym] = {
                    "price": round(float(price), 2),
                    "change": round(float(change_val), 2),
                    "changePercent": round(float(change_pct), 2),
                    "name": name,
                    "sector": sector,
                }
            except Exception:
                continue

    except Exception:
        # Fallback: fetch one by one
        for sym in tickers:
            try:
                tk = yf.Ticker(sym)
                info = tk.fast_info
                price = getattr(info, "last_price", None) or getattr(info, "regular_market_previous_close", None)
                prev_close = getattr(info, "regular_market_previous_close", None) or getattr(info, "previous_close", None)

                if price is None or price <= 0:
                    hist = tk.history(period="2d")
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])
                        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price

                if price is None or price <= 0:
                    continue

                change_val = price - prev_close if prev_close else 0
                change_pct = (change_val / prev_close * 100) if prev_close and prev_close != 0 else 0

                name = _STOCK_NAMES.get(sym, sym)
                sector = _STOCK_SECTORS.get(sym, "综合")

                results[sym] = {
                    "price": round(float(price), 2),
                    "change": round(float(change_val), 2),
                    "changePercent": round(float(change_pct), 2),
                    "name": name,
                    "sector": sector,
                }
            except Exception:
                continue

    return results


def fetch_indices_data() -> list:
    """
    Fetch current values for global market indices.

    Returns:
        list: List of dicts with keys: region, name, price, change, changePercent, up.
              Returns empty list if all fetches fail.
    """
    results = []
    tickers = [idx["ticker"] for idx in _INDICES]

    try:
        ticker_str = " ".join(tickers)
        yt = yf.Tickers(ticker_str)

        for idx_def in _INDICES:
            sym = idx_def["ticker"]
            try:
                tk = yt.tickers.get(sym)
                if tk is None:
                    continue

                info = tk.fast_info
                price = getattr(info, "last_price", None) or getattr(info, "regular_market_previous_close", None)
                prev_close = getattr(info, "regular_market_previous_close", None) or getattr(info, "previous_close", None)

                if price is None or price <= 0:
                    hist = tk.history(period="2d")
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])
                        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price

                if price is None or price <= 0:
                    continue

                change_val = price - prev_close if prev_close else 0
                change_pct = (change_val / prev_close * 100) if prev_close and prev_close != 0 else 0

                # Format large prices
                price_str = f"{price:,.2f}" if price >= 10000 else f"{price:,.2f}"

                results.append({
                    "region": idx_def["region"],
                    "name": idx_def["name"],
                    "price": price_str,
                    "change": f"{change_val:+.2f}",
                    "changePercent": f"{change_pct:+.2f}%",
                    "up": change_val >= 0,
                    "trend": _gen_mini_trend(change_val >= 0, 20),
                })
            except Exception:
                continue

    except Exception:
        pass

    return results


def get_market_stocks() -> dict:
    """Return the market stock groupings with display info."""
    return dict(_MARKETS)


def get_stock_metadata() -> dict:
    """Return combined metadata (name + sector) for all known stocks."""
    result = {}
    for sym, name in _STOCK_NAMES.items():
        result[sym] = {
            "name": name,
            "sector": _STOCK_SECTORS.get(sym, "综合"),
        }
    return result


def _gen_mini_trend(up: bool, length: int = 20) -> list:
    """Generate a mini sparkline trend based on direction."""
    random.seed(abs(hash(up)) % (2**31))
    arr = []
    v = 5.0
    bias = 0.15 if up else -0.15
    for _ in range(length):
        v += (random.random() - 0.45) * 2.0 + bias
        arr.append(round(v, 1))
    return arr


# ── Sector / Ranking / Market Summary ────────────────────────

def get_sector_groups() -> dict:
    """Return sector grouping definitions."""
    return dict(_SECTOR_GROUPS)


def fetch_gainers_losers(quotes: dict, top_n: int = 10) -> dict:
    """
    Compute top gainers and losers from real-time quotes.

    Parameters:
        quotes: Dict from fetch_realtime_quotes()
        top_n: Number of top entries per list.

    Returns:
        dict with 'gainers' and 'losers' arrays sorted by changePercent.
    """
    entries = []
    for sym, q in quotes.items():
        entries.append({
            "ticker": sym,
            "name": q.get("name", sym),
            "price": q["price"],
            "changePercent": q["changePercent"],
            "change": q["change"],
        })

    entries.sort(key=lambda x: x["changePercent"], reverse=True)

    gainers = [e for e in entries if e["changePercent"] > 0][:top_n]
    losers  = [e for e in entries if e["changePercent"] < 0]
    losers.sort(key=lambda x: x["changePercent"])
    losers = losers[:top_n]

    return {"gainers": gainers, "losers": losers}


def fetch_sector_heatmap(quotes: dict) -> list:
    """
    Aggregate sector performance from real-time quotes.

    Returns:
        list of sector dicts with {name, changePercent, stockCount, upCount, downCount}
    """
    sector_data = {}  # sector_name -> {total_change, count, up, down}
    for sym, q in quotes.items():
        sector = _STOCK_SECTORS.get(sym)
        if not sector:
            continue
        if sector not in sector_data:
            sector_data[sector] = {"total_change": 0.0, "count": 0, "up": 0, "down": 0}
        sd = sector_data[sector]
        sd["total_change"] += q["changePercent"]
        sd["count"] += 1
        if q["changePercent"] >= 0:
            sd["up"] += 1
        else:
            sd["down"] += 1

    result = []
    for name, data in sector_data.items():
        if data["count"] == 0:
            continue
        avg_change = data["total_change"] / data["count"]
        result.append({
            "name": name,
            "changePercent": round(avg_change, 2),
            "stockCount": data["count"],
            "upCount": data["up"],
            "downCount": data["down"],
        })

    result.sort(key=lambda x: x["changePercent"], reverse=True)
    return result


def get_market_summary(quotes: dict = None) -> dict:
    """
    Build a high-level market summary.

    Returns dict with:
      - total_stocks, advancing, declining, unchanged
      - average_change
      - broad_sentiment (BULLISH / BEARISH / MIXED)
    """
    if not quotes:
        return {"total_stocks": 0, "advancing": 0, "declining": 0,
                "unchanged": 0, "average_change": 0, "sentiment": "N/A"}

    adv = sum(1 for q in quotes.values() if q["changePercent"] > 0.05)
    dec = sum(1 for q in quotes.values() if q["changePercent"] < -0.05)
    unch = len(quotes) - adv - dec
    avg_chg = sum(q["changePercent"] for q in quotes.values()) / max(len(quotes), 1)

    if avg_chg > 0.5:
        sentiment = "🟢 偏多"
    elif avg_chg < -0.5:
        sentiment = "🔴 偏空"
    else:
        sentiment = "🟡 震荡"

    return {
        "total_stocks": len(quotes),
        "advancing": adv,
        "declining": dec,
        "unchanged": unch,
        "average_change": round(avg_chg, 2),
        "sentiment": sentiment,
    }
