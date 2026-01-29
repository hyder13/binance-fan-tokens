from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_FILE = "fan_tokens.json"
CACHE_SECONDS = 60 # 幣圈變化快，設 1 分鐘快取

# 權重排名
MCAP_RANK = {
    "SANTOS": 12, "LAZIO": 11, "PORTO": 10, "PSG": 9, "BAR": 8, "CITY": 7,
    "ALPINE": 6, "JUV": 5, "ACM": 4, "ATM": 3, "ASR": 2, "OG": 1
}

def analyze_token(token):
    price_change = float(token['priceChangePercent'])
    symbol = token['symbol']
    
    # 小U 的幣圈分析邏輯
    insight = ""
    if price_change > 10:
        insight = "🔥 漲幅驚人！目前動能強勁，注意止盈，不要盲目追高。"
    elif price_change > 0:
        insight = "📈 穩定上升中，可以持續關注支撐點。"
    elif price_change < -10:
        insight = "📉 跌幅較深，若看好專案價值，或許是分批佈局的機會。"
    else:
        insight = "😴 盤整中，波動度較低，適合觀望。"
    
    token['u_insight'] = insight
    return token

def fetch_binance_data():
    print("Fetching from Binance API...")
    url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        tickers = response.json()
        
        fan_symbols = list(MCAP_RANK.keys())
        results = []
        
        for ticker in tickers:
            symbol = ticker['symbol']
            if symbol.endswith('USDT'):
                base_asset = symbol[:-4]
                if base_asset in fan_symbols:
                    token_data = {
                        "symbol": base_asset,
                        "price": ticker['lastPrice'],
                        "priceChangePercent": ticker['priceChangePercent'],
                        "volume": ticker['volume'],
                        "quoteVolume": ticker['quoteVolume'],
                        "mcap": MCAP_RANK.get(base_asset, 0)
                    }
                    results.append(analyze_token(token_data))
        
        results.sort(key=lambda x: x['mcap'], reverse=True)
        # 移除排序用的 mcap 欄位
        for r in results:
            if 'mcap' in r: del r['mcap']
            
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tokens": results
        }
        
        with open(DATA_FILE, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        return output
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/tokens')
def get_tokens():
    if os.path.exists(DATA_FILE):
        file_age = time.time() - os.path.getmtime(DATA_FILE)
        if file_age < CACHE_SECONDS:
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                return jsonify(json.load(f))
    
    data = fetch_binance_data()
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port)
