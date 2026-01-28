import requests
import json
from datetime import datetime
import os
import subprocess

# 這個腳本現在只負責更新本地數據以供監控使用，不再執行 Git Push
def fetch_fan_tokens():
    print("Fetching fan tokens from Binance for local monitor...")
    url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    
    MCAP_RANK = {
        "SANTOS": 12, "LAZIO": 11, "PORTO": 10, "PSG": 9, "BAR": 8, "CITY": 7,
        "ALPINE": 6, "JUV": 5, "ACM": 4, "ATM": 3, "ASR": 2, "OG": 1
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        tickers = response.json()
        
        fan_symbols = list(MCAP_RANK.keys())
        
        results = []
        for ticker in tickers:
            symbol = ticker['symbol']
            if symbol.endswith('USDT'):
                base_asset = symbol[:-4]
                if base_asset in fan_symbols:
                    results.append({
                        "symbol": base_asset,
                        "price": ticker['lastPrice'],
                        "priceChangePercent": ticker['priceChangePercent'],
                        "volume": ticker['volume'],
                        "quoteVolume": ticker['quoteVolume'],
                        "mcap": MCAP_RANK.get(base_asset, 0)
                    })
        
        results.sort(key=lambda x: x['mcap'], reverse=True)
        for r in results:
            del r['mcap']
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "fan_tokens.json")
        
        output = {
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tokens": results
        }
        
        with open(data_file, "w") as f:
            json.dump(output, f, indent=4)
            
        print(f"Successfully updated local data for {len(results)} fan tokens.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_fan_tokens()
