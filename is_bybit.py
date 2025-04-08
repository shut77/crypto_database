import psycopg2
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
from config import host, user, password, db_name, API_SECRET1, API_KEY1, API_MARKET
import requests
import pandas as pd
import talib
import numpy as np
from sqlalchemy import create_engine, text


from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


API_KEY = API_KEY1
API_SECRET = API_SECRET1
SYMBOLS_for_bybit = ['BTCUSDT', 'ETHUSDT', 'NOTUSDT', 'PLUMEUSDT', 'OBTUSDT', 'LINKUSDT', 'OMUSDT', 'DAIUSDT',
                     'UNIUSDT', 'PEPEUSDT', 'NEARUSDT', 'ONDOUSDT', 'MNTUSDT', 'TRUMPUSDT', 'AMIUSDT', 'SUIUSDT',
                     'APEXUSDT', 'SUSDT', 'GRASSUSDT', 'WLDUSDT', 'ARBUSDT', 'WALUSDT', 'CAKEUSDT', 'AI16ZUSDT',
                     'WUSDT', 'CMETHUSDT', 'POPCATUSDT', 'RENDERUSDT', 'TIAUSDT', 'WIFUSDT', 'VIRTUALUSDT',
                     'JASMYUSDT', 'GALAUSDT', 'XTERUSDT', 'DYDXUSDT', 'ZROUSDT', 'SONICUSDT', 'INJUSDT',
                     'PENDLEUSDT', 'LDOUSDT', 'PARTIUSDT', 'C98USDT', 'JUPUSDT', 'ORDIUSDT']

SYMBOLS = ["BTC", "ETH","NOT",  "PLUME", "OBT",  "LINK", "OM",  "DAI", "UNI",
            "PEPE",  "NEAR", "ONDO", "MNT", "TRUMP" , 'AMI', "SUI", "APEX", "S", "GRASS", "WLD", "ARB", "WAL",  "CAKE",  "AI16Z",
           "W", "CMETH", "POPCAT", "RENDER", 'TIA', 'WIF', "VIRTUAL", "JASMY", "GALA", "XTER", "DYDX",  "ZRO",  "SONIC",
           "INJ", "PENDLE", "LDO", "PARTI", "C98", "JUP", "ORDI"]
INTERVAL = "60"  # 1 минута
CATEGORY = "spot"
INTERVALS = {
    "5m": "5",
    "1h": "60",
    "4h": "240",
    "1d": "D"
}

client = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET
)

#  запрос исторических свечей
def get_historical_klines(symbol, interval, start_time, end_time):
    try:
        response = client.get_kline(
            category=CATEGORY,
            symbol=symbol,
            interval=interval,
            start=start_time * 1000,  # в миллисекунды
            end=end_time * 1000
        )
        print(f"Response for {symbol}:", response)

        if response.get("retCode") == 0:
            data = response.get("result", {}).get("list", [])
            if not data:
                print(f"No data for {symbol}")
            return data
        else:
            print(f"API Error for {symbol}: {response.get('retMsg')}")
            return []
    except Exception as e:
        print(f"API Exception for {symbol}: {e}")
        return []





SYMBOLS = ["BTC", "ETH","NOT", "PLUME", "OBT", "XRP", "BNB", "SOL", "DOGE",
           "TRX", "ADA", "LEO", "LINK", "AVAX", "OM", "DOT", "DAI", "LTC", "UNI",
           "OKB", "PEPE", "APT", "NEAR", "ONDO", "MNT", "ICP", "CRO", "KAS", "TRUMP"]


SYMBOLS = ["BTC", "ETH","NOT",  "PLUME", "OBT",  "LINK", "OM",  "DAI", "UNI",
            "PEPE",  "NEAR", "ONDO", "MNT", "TRUMP" , 'AMI', "SUI", "APEX", "S", "GRASS", "WLD", "ARB", "WAL",  "CAKE",  "AI16Z",
           "W", "CMETH", "POPCAT", "RENDER", 'TIA', 'WIF', "VIRTUAL", "JASMY", "GALA", "XTER", "DYDX",  "ZRO",  "SONIC",
           "INJ", "PENDLE", "LDO", "PARTI", "C98", "JUP", "ORDI"]



s2 = [symbol + "USDT" for symbol in SYMBOLS]
print(s2)

def save_to_database(data, symbol):
    try:
        #(удаляем 'USDT' из конца)
        base_symbol = symbol.replace('USDT', '')

        with psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as conn:
            with conn.cursor() as cursor:
                #  ID токена по БАЗОВОМУ символу
                cursor.execute("SELECT id FROM all_token WHERE symbol = %s", (base_symbol,))
                token_row = cursor.fetchone()

                if not token_row:
                    print(f"Token {base_symbol} (from {symbol}) not found in all_token table. Skipping.")
                    return

                token_id = token_row[0]


                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historical_prices (
                        token_id INTEGER NOT NULL,
                        timestamp TIMESTAMP,
                        open DECIMAL,
                        high DECIMAL,
                        low DECIMAL,
                        close DECIMAL,
                        volume DECIMAL,
                        FOREIGN KEY (token_id) REFERENCES all_token(id),
                        UNIQUE(token_id, timestamp)
                    )
                """)

                data_tuples = [
                    (
                        token_id,
                        datetime.fromtimestamp(int(item[0]) / 1000),
                        float(item[1]),
                        float(item[2]),
                        float(item[3]),
                        float(item[4]),
                        float(item[5])
                    )
                    for item in data
                ]

                cursor.executemany("""
                    INSERT INTO historical_prices 
                    (token_id, timestamp, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (token_id, timestamp) DO NOTHING
                """, data_tuples)

                conn.commit()
                print(f"Inserted {len(data)} price records for {symbol} (token: {base_symbol})")

    except Exception as e:
        print(f"Database error for {symbol}: {str(e)}")


import time


def in_coinmarketcap():
    tic = []
    last_request_time = 0  # Время последнего запроса

    for symbol in SYMBOLS:
        try:
            # 1. Сначала пробуем получить данные из CoinMarketCap
            coin_data = None

            if API_MARKET:
                try:
                    # когда был последний запрос
                    current_time = time.time()
                    if current_time - last_request_time < 10:
                        wait_time = 10 - (current_time - last_request_time)
                        print(f"Ожидание {wait_time:.1f} секунд перед следующим запросом...")
                        time.sleep(wait_time)

                    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_MARKET}

                    # информацию о токене
                    info_response = requests.get(
                        "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info",
                        headers=headers,
                        params={"symbol": symbol, "aux": "urls,description,logo,date_added"},
                        timeout=5000
                    )
                    info_response.raise_for_status()
                    info_data = info_response.json()

                    # Обновляем время последнего запроса
                    last_request_time = time.time()

                    # котировки (тоже учитываем лимит)
                    current_time = time.time()
                    if current_time - last_request_time < 10:
                        wait_time = 10 - (current_time - last_request_time)
                        print(f"Ожидание {wait_time:.1f} секунд перед запросом котировок...")
                        time.sleep(wait_time)

                    quotes_response = requests.get(
                        "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
                        headers=headers,
                        params={"symbol": symbol, "convert": "USD"},
                        timeout=5000
                    )
                    quotes_response.raise_for_status()
                    quotes_data = quotes_response.json()

                    last_request_time = time.time()

                    # Если монета найдена в CoinMarketCap
                    if symbol in info_data.get('data', {}) and symbol in quotes_data.get('data', {}):
                        coin_info = info_data["data"][symbol][0]
                        coin_quotes = quotes_data["data"][symbol][0]

                        coin_data = (
                            coin_info['symbol'],
                            coin_info['name'],
                            coin_info.get('date_added'),

                            coin_quotes.get('platform', {}).get('name'),
                            coin_info['urls']['website'][0] if coin_info['urls']['website'] else None,
                            coin_info.get('description')
                        )
                        print(f"✓ Данные для {symbol} получены из CoinMarketCap")

                except Exception as cmc_error:
                    print(f"Ошибка CoinMarketCap для {symbol}: {str(cmc_error)}")

            # 2. Если не получили данные из CoinMarketCap, пробуем CoinGecko
            if coin_data is None:
                try:
                    gecko_id = {
                        "BTC": "bitcoin",
                        "ETH": "ethereum",
                        "TON": "the-open-network",
                        "ZEC": "zcash",
                    }.get(symbol, symbol.lower())

                    gecko_response = requests.get(
                        f"https://api.coingecko.com/api/v3/coins/{gecko_id}",
                        params={"localization": "false", "tickers": "false", "market_data": "false"},
                        timeout=5000
                    )

                    if gecko_response.status_code == 200:
                        gecko_data = gecko_response.json()

                        coin_data = (
                            gecko_data['symbol'].upper(),
                            gecko_data['name'],
                            gecko_data.get('genesis_date'),
                            gecko_data.get('asset_platform_id'),
                            gecko_data['links']['homepage'][0] if gecko_data['links']['homepage'] else None,
                            gecko_data['description']['en'] if 'description' in gecko_data else None
                        )
                        print(f"✓ Данные для {symbol} получены из CoinGecko")
                    else:
                        print(f"Монета {symbol} не найдена в CoinGecko")

                except Exception as gecko_error:
                    print(f"Ошибка CoinGecko для {symbol}: {str(gecko_error)}")


            if coin_data:
                tic.append(coin_data)
            else:
                print(f"× Не удалось получить данные для {symbol}")

        except Exception as e:
            print(f"Критическая ошибка для {symbol}: {str(e)}")
            continue

    return tic

def table_token(tic):
    try:
        with psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
        ) as conn:
            with conn.cursor() as cursor:
                # Создаем таблицу токенов (если её нет)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS all_token (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        date_launched TIMESTAMP,
                        platform VARCHAR(50),
                        website VARCHAR(255),
                        description TEXT
                    )
                """)

                # Вставляем данные о токенах
                cursor.executemany("""
                    INSERT INTO all_token 
                    (symbol, name, date_launched, platform, website, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO NOTHING
                """, tic)

                conn.commit()
                print(f"Inserted/updated {len(tic)} tokens")

    except Exception as e:
        print(f"Database error: {str(e)}")


class CryptoDataProcessor:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{db_name}')
        self.scalers = {}
        self._create_tables()

    def _create_tables(self):

        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS historical_prices (
                    token_id INTEGER,
                    timestamp TIMESTAMP,
                    open DECIMAL,
                    high DECIMAL,
                    low DECIMAL,
                    close DECIMAL,
                    volume DECIMAL,
                    FOREIGN KEY (token_id) REFERENCES all_token(id),
                    UNIQUE(token_id, timestamp)
                    )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS market_indicators (
                    token_id INTEGER,
                    timestamp TIMESTAMP,
                    rsi DECIMAL,
                    macd DECIMAL,
                    macd_signal DECIMAL,
                    FOREIGN KEY (token_id) REFERENCES all_token(id),
                    UNIQUE(token_id, timestamp)
                    )
            """))

    def fetch_candles(self, symbol, interval, limit=2000):

        try:
            resp = client.get_kline(
                category="spot",
                symbol=f"{symbol}USDT",
                interval=interval,
                limit=limit
            )

            if resp['retCode'] != 0:
                print(f"Error fetching data for {symbol}: {resp['retMsg']}")
                return None

            #  все колонки из ответа
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            df = pd.DataFrame(resp['result']['list'], columns=columns)

            # Удаляем лишнюю колонку turnover
            df = df.drop(columns=['turnover'])

            # Конвертация типов
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].astype(float)

            # Расчет индикаторов
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])

            return df

        except Exception as e:
            print(f"Error in fetch_candles for {symbol}: {str(e)}")
            return None

    def save_to_db(self, df, symbol):

        base_symbol = symbol.replace('USDT', '')

        try:
            with self.engine.begin() as conn:

                token_id = conn.execute(
                    text("SELECT id FROM all_token WHERE symbol = :symbol"),
                    {"symbol": base_symbol}
                ).scalar()

                if not token_id:
                    raise ValueError(f"Token {base_symbol} not found")


                historical_data = [{
                    "token_id": token_id,
                    "timestamp": row['timestamp'],
                    "open": row['open'],
                    "high": row['high'],
                    "low": row['low'],
                    "close": row['close'],
                    "volume": row['volume']
                } for _, row in df.iterrows()]

                conn.execute(
                    text("""
                        INSERT INTO historical_prices 
                        (token_id, timestamp, open, high, low, close, volume)
                        VALUES (:token_id, :timestamp, :open, :high, :low, :close, :volume)
                        ON CONFLICT (token_id, timestamp) DO NOTHING
                    """),
                    historical_data
                )


                indicator_data = [{
                    "token_id": token_id,
                    "timestamp": row['timestamp'],
                    "rsi": row['rsi'],
                    "macd": row['macd'],
                    "macd_signal": row['macd_signal']
                } for _, row in df.iterrows()]

                conn.execute(
                    text("""
                        INSERT INTO market_indicators 
                        (token_id, timestamp, rsi, macd, macd_signal)
                        VALUES (:token_id, :timestamp, :rsi, :macd, :macd_signal)
                        ON CONFLICT (token_id, timestamp) DO UPDATE
                        SET rsi = EXCLUDED.rsi,
                            macd = EXCLUDED.macd,
                            macd_signal = EXCLUDED.macd_signal
                    """),
                    indicator_data
                )

            print(f"Data successfully saved for {symbol}")
            return True

        except Exception as e:
            print(f"Error saving data for {symbol}: {str(e)}")
            return False

    def prepare_training_data(self, symbol, lookback=168, horizon=3):

        try:

            with self.engine.connect() as conn:
                exists = conn.execute(
                    text("""
                        SELECT 1 
                        FROM market_indicators 
                        LIMIT 1
                    """)
                ).scalar()

                if not exists:
                    raise ValueError("No data in market_indicators table")

            query = text("""
                SELECT p.timestamp, p.close, p.volume, 
                       m.rsi, m.macd, m.macd_signal
                FROM historical_prices p
                JOIN market_indicators m ON p.token_id = m.token_id AND p.timestamp = m.timestamp
                JOIN all_token t ON p.token_id = t.id
                WHERE t.symbol = :symbol
                ORDER BY p.timestamp
            """)

            df = pd.read_sql(query, self.engine, params={"symbol": symbol})

            if df.empty:
                raise ValueError("No training data available")

            # Обработка пропущенных значений
            df = df.fillna(method='ffill').fillna(method='bfill')

            # Нормализация
            features = ['close', 'volume', 'rsi', 'macd', 'macd_signal']
            self.scalers[symbol] = MinMaxScaler()
            scaled = self.scalers[symbol].fit_transform(df[features])

            # Формирование окон
            X, y = [], []
            for i in range(lookback, len(scaled) - horizon):
                X.append(scaled[i - lookback:i])
                y.append(scaled[i:i + horizon, 0])

            return np.array(X), np.array(y)

        except Exception as e:
            print(f"Error preparing training data: {str(e)}")
            return None, None


class SimpleForecastModel:
    def __init__(self, input_shape, horizon):
        self.model = Sequential([
            LSTM(64, input_shape=input_shape),
            Dense(horizon)
        ])
        self.model.compile(optimizer='adam', loss='mse')

    def train(self, X, y, epochs=1000, batch_size=32):
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2)
        return history

def main():


    # 1.  получаем и сохраняем информацию о токенах
    token_info = in_coinmarketcap()
    table_token(token_info)

    # 2. получаем и сохраняем исторические данные
    end_time = int(datetime.now().timestamp())
    start_time = end_time - 45*86400  # 24 часа назад

    for symbol in SYMBOLS_for_bybit:
        klines = get_historical_klines(symbol, INTERVAL, start_time, end_time)
        if klines:
            print(f"Saving {len(klines)} records for {symbol}")
            save_to_database(klines, symbol)
        else:
            print(f"No data received for {symbol}")

    processor = CryptoDataProcessor()

    # Сбор и сохранение данных
    for symbol in SYMBOLS:
        print(f"Processing {symbol}...")
        df = processor.fetch_candles(symbol, INTERVALS["1h"])
        if df is not None:
            if not processor.save_to_db(df, symbol):
                print(f"Skipping {symbol} due to save error")

    # Подготовка и обучение модели
    try:
        X, y = processor.prepare_training_data("BTC")
        if X is not None and y is not None:
            model = SimpleForecastModel(X.shape[1:], y.shape[1])
            model.train(X, y)

            # Прогнозирование
            last_window = X[-1].reshape(1, *X.shape[1:])
            prediction = model.model.predict(last_window)

            # Обратное преобразование
            if 'BTC' in processor.scalers:
                dummy = np.zeros((prediction.shape[1], 5))
                dummy[:, 0] = prediction[0]
                predicted_prices = processor.scalers['BTC'].inverse_transform(dummy)[:, 0]
                print(f"Predicted prices for BTC: {predicted_prices}")
    except Exception as e:
        print(f"Main process error: {str(e)}")





if __name__ == "__main__":
    main()

