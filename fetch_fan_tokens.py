import requests
import json
from datetime import datetime
import os

def fetch_fan_tokens():
    print("Fetching fan tokens from Binance...")
    # 使用 Binance 24hr ticker API
    url = "https://api.binance.com/api/v3/ticker/24hr"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json()
        
        # 粉絲代幣清單 (常見的幣安粉絲代幣)
        # 通常這些代幣是以 USDT 交易對的形式存在
        # 例如: LAZIO, PORTO, SANTOS, ALPINE, BAR, CITY, PSG, ATM, ACM, JUV, OGO, ASRE
        # 由於 Binance 沒有直接的 "Fan Token" 分類 API，我們過濾出已知的符號
        fan_symbols = [
            "LAZIO", "PORTO", "SANTOS", "ALPINE", "BAR", "CITY", 
            "PSG", "ATM", "ACM", "JUV", "OG", "ASR"
        ]
        
        results = []
        for ticker in tickers:
            symbol = ticker['symbol']
            # 只抓取 USDT 交易對
            if symbol.endswith('USDT'):
                base_asset = symbol[:-4]
                if base_asset in fan_symbols:
                    results.append({
                        "symbol": base_asset,
                        "price": ticker['lastPrice'],
                        "priceChangePercent": ticker['priceChangePercent'],
                        "volume": ticker['volume'],
                        "quoteVolume": ticker['quoteVolume']
                    })
        
        # 按字母排序
        results.sort(key=lambda x: x['symbol'])
        
        data_file = "fan_tokens.json"
        output = {
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tokens": results
        }
        
        with open(data_file, "w") as f:
            json.dump(output, f, indent=4)
            
        print(f"Successfully fetched {len(results)} fan tokens.")
        for t in results:
            print(f"{t['symbol']}: {t['price']} ({t['priceChangePercent']}%)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_fan_tokens()
