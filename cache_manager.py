import pickle
import time
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_TTL = 23 * 3600  # 23 hours — refresh after market closes


def _path(ticker: str) -> Path:
    return CACHE_DIR / f"{ticker.upper()}.pkl"


def load(ticker: str) -> dict | None:
    p = _path(ticker)
    if not p.exists():
        return None
    if time.time() - p.stat().st_mtime > CACHE_TTL:
        return None
    with open(p, "rb") as f:
        return pickle.load(f)


def save(ticker: str, data: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    with open(_path(ticker), "wb") as f:
        pickle.dump(data, f)


def cached_tickers() -> list[str]:
    if not CACHE_DIR.exists():
        return []
    return [p.stem for p in CACHE_DIR.glob("*.pkl")]
