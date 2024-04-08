from datetime import datetime, timedelta
import logging
import sys

import asyncio
from aiohttp import ClientSession, ClientConnectorError

async def request(url: str):
    async with ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.ok:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None
       
def pb_handler(data, valute = None):
    EXCHANGE_RATE = data['exchangeRate']
    DATE = data['date'] 
    try:
        if not valute:
            usd, = list(filter(lambda el: el['currency'] == "USD", EXCHANGE_RATE))
            S_USD, P_USD = usd['saleRateNB'], usd['purchaseRateNB']
            eur, = list(filter(lambda el: el['currency'] == "EUR", EXCHANGE_RATE))
            S_EUR, P_EUR = eur['saleRateNB'], eur['purchaseRateNB']
            return {DATE:{'EUR': {'sale': S_EUR , 'purchase': P_EUR }, 'USD': {'sale': S_USD, 'purchase': P_USD}}}
        else:
            for elem in EXCHANGE_RATE:
                if elem['currency'] == valute:
                    SALE, PURCHASE = elem['saleRateNB'], elem['purchaseRateNB']
                    return {DATE: {elem['currency']:{'sale': SALE, 'purchase': PURCHASE }}}
            print('Valute not found')
            raise 'Valute not found'
    except ValueError:
            print('Error: No information')

async def get_exchange(url, handler, valute = None):
    result = await request(url)
    if result and valute:
        return handler(result, valute)
    elif result:
        return handler(result)
    return "Failed to retrieve data"

def url_creator(inp:int = 0):
    return fr'https://api.privatbank.ua/p24api/exchange_rates?date={(datetime.today().date() - timedelta(int(inp))).strftime("%d.%m.%Y")}'

async def start(data: list = []):
    result = []
    days = 0
    valute = str()
    if not data:
        data = sys.argv
    else:
        data.insert(0,'')
    if len(data) > 3 or len(data) < 1:
        print('Error:')
        return
    elif len(data) == 1:
        URL = url_creator()
        result.append(await get_exchange(URL, pb_handler))
        print(result)
        return result
    
    if data[1].isdigit():
        num = int(data[1])
        if num <= 10 and num >= 0:
            days = num
        else:
            print(f"Input nomber must be in range 1-10")
            return "Input nomber must be in range 1-10"
    else:
        if len(data[1]) == 3:
            valute = data[1]
        else:
            print('Wrong arguments.')
            return 'Wrong arguments.'
    
    if days and len(data) == 3:
        if len(data[2]) == 3:
            valute = data[2]
        else:
            print('Wrong arguments.')
            return 'Wrong arguments.'
    if days:
        for day in range(days):
            URL = url_creator(days - 1)
            result.append(await get_exchange(URL, pb_handler, valute.upper()))
            days -= 1
    else:
        URL = url_creator(days)
        result.append(await get_exchange(URL, pb_handler, valute.upper()))

    print(result)
    return result


if __name__ == '__main__':
    asyncio.run(start())

