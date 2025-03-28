import psycopg2
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
from config import host, user, password, db_name, API_SECRET1, API_KEY1, API_MARKET
import requests


API_KEY = API_KEY1
API_SECRET = API_SECRET1
SYMBOLS_for_bybit = ["NOTUSDT", "PLUMEUSDT", "OBTUSDT"]
INTERVAL = "60"  # 1 минута
CATEGORY = "spot"


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
        print(f"Response for {symbol}:", response)  # Отладка

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



# Константы
SYMBOLS = ["NOT", "PLUME", "OBT"]


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


def in_coinmarketcap():
    tic = []
    for symbol in SYMBOLS:
        try:
            API_KEY = API_MARKET
            headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY}

            # Получаем информацию о токене
            info_response = requests.get(
                "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info",
                headers=headers,
                params={"symbol": symbol, "aux": "urls,description,logo,date_added"}
            )
            info_response.raise_for_status()
            info_data = info_response.json()

            # Получаем котировки
            quotes_response = requests.get(
                "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
                headers=headers,
                params={"symbol": symbol, "convert": "USD"}
            )
            quotes_response.raise_for_status()
            quotes_data = quotes_response.json()

            # Обрабатываем данные
            coin_info = info_data["data"][symbol][0]
            coin_quotes = quotes_data["data"][symbol][0]

            platform = coin_quotes.get('platform', {}).get('name', None)
            website = coin_info['urls']['website'][0] if coin_info['urls']['website'] else None

            tic.append((
                coin_info['symbol'],
                coin_info['name'],
                coin_info.get('date_launched'),
                platform,
                website,
                coin_info.get('description')
            ))

        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")

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


def main():
    # 1. Сначала получаем и сохраняем информацию о токенах
    token_info = in_coinmarketcap()
    table_token(token_info)

    # 2. Затем получаем и сохраняем исторические данные
    end_time = int(datetime.now().timestamp())
    start_time = end_time - 86400  # 24 часа назад

    for symbol in SYMBOLS_for_bybit:
        klines = get_historical_klines(symbol, INTERVAL, start_time, end_time)
        if klines:
            print(f"Saving {len(klines)} records for {symbol}")
            save_to_database(klines, symbol)
        else:
            print(f"No data received for {symbol}")





if __name__ == "__main__":
    main()
