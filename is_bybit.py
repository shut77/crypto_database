import psycopg2
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
from config import host, user, password, db_name
import requests

API_KEY = "kyq"
API_SECRET = "CtG"
SYMBOLS = ["PLUMEUSDT", "ETHUSDT"]
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



def save_to_database(data, symbol):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = connection.cursor()

        # Создание таблицы, если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_prices (
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open DECIMAL,
                high DECIMAL,
                low DECIMAL,
                close DECIMAL,
                volume DECIMAL,
                UNIQUE(symbol, timestamp)
            )
        """)
        # Обработка данных
        data_tuples = [
            (
                symbol,
                datetime.fromtimestamp(int(item[0]) / 1000),  # Время в секундах
                float(item[1]),  # Open
                float(item[2]),  # High
                float(item[3]),  # Low
                float(item[4]),  # Close
                float(item[5])   # Volume
            )
            for item in data
        ]

        # Вставка данных
        cursor.executemany("""
            INSERT INTO historical_prices 
            (symbol, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        """, data_tuples)

        connection.commit()
        print(f"Inserted {len(data)} records for {symbol}")

    except Exception as ex:
        print(f"Database Error for {symbol}: {ex}")
    finally:
        if connection:
            cursor.close()
            connection.close()




def in_coinmarketcap():
    tic = []
    SYMBOLS = ["NOT", "PLUME", "OBT"]
    for symbol in SYMBOLS:

        API_KEY = "********"

        url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": API_KEY
        }
        params = {
            "symbol": symbol,
            "aux": "urls,description,logo,date_added"

        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        #СЛЕДУЮЩИЕ ДАННЫЕ
        url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": API_KEY
        }
        params = {
            "symbol": symbol,
            "convert": "USD"

        }
        response2 = requests.get(url, headers=headers, params=params)
        data2 = response2.json()






        if (response.status_code == 200) and (response2.status_code == 200):
            coin_data2 = data2["data"][symbol][0]

            if coin_data2.get("platform"):
                platform_token = coin_data2['platform']['name']
            else:
                platform_token = "Null"

            print(platform_token)


            coin_data = data["data"][symbol][0]
            tic.append((coin_data['symbol'],
                        coin_data['name'],
                        coin_data['date_launched'],
                        platform_token,
                        coin_data['urls']['website'][0],
                        coin_data['description']))
        else:
            print(f"Ошибка: {data['status']['error_message']}")

    return tic

def table_token(tic):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = connection.cursor()

        # Создание таблицы, если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS all_token (
                id SERIAL PRIMARY KEY,
                short_name VARCHAR(10),
                symbol VARCHAR(50) NOT NULL,
                data_launched VARCHAR(60) NOT NULL,
                platforma VARCHAR(50),
                url_adress VARCHAR(50),
                information VARCHAR(1000)

            )
        """)

        data_is_coinmarket = [
            (
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                item[5]

            )
            for item in tic
        ]
        # Вставка
        cursor.executemany("""
            INSERT INTO all_token
            (short_name, symbol, data_launched, platforma, url_adress, information)
            VALUES (%s, %s,%s, %s, %s, %s)

        """, data_is_coinmarket)

        connection.commit()
    except Exception as ex:
        print(f"Database Error for {tic[0]}: {ex}")
    finally:
        if connection:
            cursor.close()
            connection.close()



def main():
    #ТАБЛИЦА ИСТОРИЧЕСКИХ ДАННЫХ
    end_time = int(datetime.now().timestamp())  # Текущее время (секунды)
    start_time = end_time - 86400  # 24 часа назад

    for symbol in SYMBOLS:
        klines = get_historical_klines(symbol, INTERVAL, start_time, end_time)
        if klines:
            print(f"Saving {len(klines)} records for {symbol}")
            save_to_database(klines, symbol)
        else:
            print(f"No data received for {symbol}")



    #ТАБЛИЦА ВСЕХ МОНЕТ С ИНФОРМАЦИЕЙ
    info_is_coinmarket = in_coinmarketcap()
    table_token(info_is_coinmarket)


    #ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ И ИХ КОШЕЛЬКОВ




if __name__ == "__main__":
    main()
