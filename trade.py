
import datetime
import json
import time

import psycopg2
import psycopg2.extras
import pytz
import requests

import settings


# get amount of money i have for all currencies in currency pairs (-> save: anzahl währungen)

# if there is no present data of the currency pair and i have budget in it something is wrong! error email.

# if there is a buy signal:
    # nimm den (1/anzahl währungen)ten teil des budgets von secondary currency und erstelle kauf order

# elif there is a sell signal.
    # add sell order of all of primary_currency

#####################################################################

PRICE_TYPE_NAME = 'Limit'
LIMIT_MARGIN_PERCENTAGE = 0.0

AUTH_IDS_CACHE = {}
EXCHANGE_IDS_CACHE = {}
MARKET_IDS_CACHE = {}
ORDER_TYPE_IDS_CACHE = {}
PRICE_TYPE_ID_CACHE = None

BUY = 'Buy'  # do not change
SELL = 'Sell'  # do not change

COINIGY_HEADERS = {
    'Content-Type': 'application/json',
    'X-API-KEY': settings.COINIGY_API_KEY,
    'X-API-SECRET': settings.COINIGY_API_SECRET,
}


def get_trading_decision(exchange_code, primary_currency, secondary_currency):
    """
    Decides if for the given currency pair on the given exchange we should buy or sell.
    This is done with a simple rolling averages algorithm.
    """
    SHORT_AVG_COUNT = 5
    LONG_AVG_COUNT = 15

    TIME_FRAME_IN_MINUTES = 3 * LONG_AVG_COUNT

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    reference_time = (now - datetime.timedelta(minutes=TIME_FRAME_IN_MINUTES)).replace(second=0, microsecond=0)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT time, exchange_code, primary_currency, secondary_currency, price
                   FROM prices_1m
                   WHERE time > %(reference_time)s AND
                         exchange_code = %(exchange_code)s AND
                         primary_currency = %(primary_currency)s AND
                         secondary_currency = %(secondary_currency)s
                   ORDER BY time ASC""", {
        'reference_time': reference_time,
        'exchange_code': exchange_code,
        'primary_currency': primary_currency,
        'secondary_currency': secondary_currency,
    })
    rows = cur.fetchall()

    short_avg = {}
    long_avg = {}

    # calculate all the rolling averages for time frame
    for idx, row in enumerate(rows):
        if idx > SHORT_AVG_COUNT:
            total = 0
            for x in range(0, SHORT_AVG_COUNT):
                total = total + rows[idx-x]['price']
            short_avg[idx] = total/SHORT_AVG_COUNT

        if idx > LONG_AVG_COUNT:
            total = 0
            for x in range(0, LONG_AVG_COUNT):
                total = total + rows[idx-x]['price']
            long_avg[idx] = total/LONG_AVG_COUNT

    # calculate buy/sell decisions for time frame
    action = ''
    for idx, row in enumerate(rows):
        if idx > LONG_AVG_COUNT:
            now = idx
            before = idx-1

            action = ''
            try:
                short_avg_moves_above_long_avg = short_avg[before] < long_avg[before] and \
                                                short_avg[now] >= long_avg[now]
                if short_avg_moves_above_long_avg:
                    action = BUY

                short_avg_moves_below_long_avg = short_avg[before] > long_avg[before] and \
                                                 short_avg[now] <= long_avg[now]
                if short_avg_moves_below_long_avg:
                    action = SELL
            except:
                pass

            print('- {}: {}: {}'.format(row['time'], row['price'], action))

    return action or None


def get_exchange_id(exchange_code):
    global EXCHANGE_IDS_CACHE

    if exchange_code not in EXCHANGE_IDS_CACHE:
        r = requests.post(settings.COINIGY_API_BASE_URL + 'exchanges', headers=COINIGY_HEADERS)
        data = json.loads(r.content.decode('utf-8'))
        for item in data['data']:
            if item['exch_code'] == exchange_code:
                EXCHANGE_IDS_CACHE[exchange_code] = int(item['exch_id'])
                break

    return EXCHANGE_IDS_CACHE[exchange_code]


def get_auth_id(exchange_code):
    global AUTH_IDS_CACHE

    if exchange_code not in AUTH_IDS_CACHE:
        r = requests.post(settings.COINIGY_API_BASE_URL + 'accounts', headers=COINIGY_HEADERS)
        data = json.loads(r.content.decode('utf-8'))
        for item in data['data']:
            if item['exch_id'] == str(get_exchange_id(exchange_code)):
                AUTH_IDS_CACHE[exchange_code] = int(item['auth_id'])
                break

    return AUTH_IDS_CACHE[exchange_code]


def get_market_id(exchange_code, primary_currency, secondary_currency):
    global MARKET_IDS_CACHE

    key = '{}-{}-{}'.format(exchange_code, primary_currency, secondary_currency)
    market_name = '{}/{}'.format(primary_currency.upper(), secondary_currency.upper())

    if key not in MARKET_IDS_CACHE:
        payload = {
            'exchange_code': exchange_code,
        }
        r = requests.post(settings.COINIGY_API_BASE_URL + 'markets',
                          headers=COINIGY_HEADERS, data=json.dumps(payload))
        data = json.loads(r.content.decode('utf-8'))

        for item in data['data']:
            if item['exch_code'] == exchange_code and item['mkt_name'] == market_name:
                MARKET_IDS_CACHE[key] = int(item['mkt_id'])
                break

    return MARKET_IDS_CACHE[key]


def get_order_type_id(order_type):
    global ORDER_TYPE_IDS_CACHE
    global PRICE_TYPE_ID_CACHE

    if order_type not in ORDER_TYPE_IDS_CACHE:
        r = requests.post(settings.COINIGY_API_BASE_URL + 'orderTypes',
                          headers=COINIGY_HEADERS)
        data = json.loads(r.content.decode('utf-8'))

        for item in data['data']['order_types']:
            if item['name'] == order_type:
                ORDER_TYPE_IDS_CACHE[order_type] = int(item['order_type_id'])
                break

        for item in data['data']['price_types']:
            if item['name'] == PRICE_TYPE_NAME:
                PRICE_TYPE_ID_CACHE = int(item['price_type_id'])
                break

    return ORDER_TYPE_IDS_CACHE[order_type]


def get_price_type_id():
    global PRICE_TYPE_ID_CACHE

    if not PRICE_TYPE_ID_CACHE:
        r = requests.post(settings.COINIGY_API_BASE_URL + 'orderTypes',
                          headers=COINIGY_HEADERS)
        data = json.loads(r.content.decode('utf-8'))

        for item in data['data']['price_types']:
            if item['name'] == PRICE_TYPE_NAME:
                PRICE_TYPE_ID_CACHE = int(item['price_type_id'])
                break

    return PRICE_TYPE_ID_CACHE


def get_current_price(exchange_code, order_type, primary_currency, secondary_currency):
    price = None

    market_name = '{}/{}'.format(primary_currency.upper(), secondary_currency.upper())

    payload = {
        'exchange_code': exchange_code,
        'exchange_market': market_name,
    }
    r = requests.post(settings.COINIGY_API_BASE_URL + 'ticker',
                      headers=COINIGY_HEADERS, data=json.dumps(payload))
    data = json.loads(r.content.decode('utf-8'))

    for item in data['data']:
        if order_type == SELL:
            bid_price = float(item['bid'])
            price = bid_price - bid_price*(LIMIT_MARGIN_PERCENTAGE/100.0)
            print('bid: %s / selling limit price: %s' % (bid_price, price))
            print('-----------------------------------------------------------------------')
            break

        elif order_type == BUY:
            ask_price = float(item['ask'])
            price = ask_price + ask_price*(LIMIT_MARGIN_PERCENTAGE/100.0)
            print('ask: %s / buying limit price: %s' % (ask_price, price))
            print('-----------------------------------------------------------------------')
            break

    for market in settings.TRADING_MARKETS:
        if market['exchange_code'] == exchange_code and \
           market['primary_currency'] == primary_currency and \
           market['secondary_currency'] == secondary_currency:
            price = round(price, market['decimal_precision'])
            break

    return price


def create_order(exchange_code, order_type, primary_currency, secondary_currency, quantity):
    auth_id = get_auth_id(exchange_code)
    exchange_id = get_exchange_id(exchange_code)
    market_id = get_market_id(exchange_code, primary_currency, secondary_currency)
    order_type_id = get_order_type_id(order_type)
    price_type_id = get_price_type_id()

    price = get_current_price(exchange_code, order_type, primary_currency, secondary_currency)

    if order_type == BUY: # convert to quantity in primary_currency
        quantity = quantity/price

    payload = {
        'auth_id': auth_id,
        'exch_id': exchange_id,
        'mkt_id': market_id,
        'order_type_id': order_type_id,
        'price_type_id': price_type_id,
        'limit_price': price,
        'order_quantity': quantity,
    }

    print('--------- addOrder! ---------------------------------------------------')
    from pprint import pprint
    pprint(payload)
    print('-----------------------------------------------------------------------')

    r = requests.post(settings.COINIGY_API_BASE_URL + 'addOrder',
                      headers=COINIGY_HEADERS, data=json.dumps(payload))
    data = json.loads(r.content.decode('utf-8'))
    pprint(data)
    print('-----------------------------------------------------------------------')
    print('')

    # if it is a sell, calculate the profit (be it positive or negative)
    profit = None
    if order_type == SELL:
        cur.execute("""SELECT price FROM trades
                                    WHERE exchange_code=%(exchange_code)s AND
                                          amount_currency=%(amount_currency)s AND
                                          price_currency=%(price_currency)s AND
                                          trade_type=%(trade_type)s
                                    ORDER BY time DESC LIMIT 1;""", {
            'exchange_code': exchange_code,
            'amount_currency': primary_currency,
            'price_currency': secondary_currency,
            'trade_type': BUY,
        })
        rows = cur.fetchall()
        buy_price = float(rows[0][0])
        profit = quantity*price - quantity*buy_price

    # save trade (including profit if it is a sell) in our database
    cur.execute("""INSERT INTO trades(time, trade_type, exchange_code,
                                      amount, amount_currency,
                                      price, price_currency,
                                      profit)
                          VALUES (%(time)s, %(trade_type)s, %(exchange_code)s,
                                  %(amount)s, %(amount_currency)s,
                                  %(price)s, %(price_currency)s,
                                  %(profit)s);""", {
        'time': datetime.datetime.now(datetime.timezone.utc),
        'trade_type': order_type,
        'exchange_code': exchange_code,
        'amount': quantity,
        'amount_currency': primary_currency,
        'price': price,
        'price_currency': secondary_currency,
        'profit': profit,
    })
    conn.commit()
    conn.close()


def fetch_current_balances(exchange_code):
    balances = {}
    auth_id = get_auth_id(exchange_code)

    payload = {
        'auth_ids': str(auth_id)
    }
    r = requests.post(settings.COINIGY_API_BASE_URL + 'balances',
                      headers=COINIGY_HEADERS, data=json.dumps(payload))
    data = json.loads(r.content.decode('utf-8'))
    for item in data['data']:
        balances[item['balance_curr_code']] = float(item['balance_amount_avail'])

    return balances


def buy(exchange_code, primary_currency, secondary_currency):
    balances = fetch_current_balances(exchange_code)

    # decide how much to spent
    try:
        quantity = balances[secondary_currency]*0.9/float(len(settings.TRADING_MARKETS))
    except KeyError:
        quantity = 0

    # create order
    if quantity:
        create_order(exchange_code, BUY, primary_currency, secondary_currency, quantity)


def sell(exchange_code, primary_currency, secondary_currency):
    balances = fetch_current_balances(exchange_code)

    # decide how much to spent
    try:
        quantity = balances[primary_currency]
    except KeyError:
        quantity = 0

    # create order
    if quantity:
        create_order(exchange_code, SELL, primary_currency, secondary_currency, quantity)


def main():
    for market in settings.TRADING_MARKETS:
        primary_currency = market['primary_currency']
        secondary_currency = market['secondary_currency']
        exchange_code = market['exchange_code']

        print('----- MARKET {}/{} --------------------------------------------------'.format(primary_currency, secondary_currency))
        action = get_trading_decision(exchange_code, primary_currency, secondary_currency)

        if action == BUY:
            buy(exchange_code, primary_currency, secondary_currency)
        elif action == SELL:
            sell(exchange_code, primary_currency, secondary_currency)


if __name__ == '__main__':
    connection_string = "dbname='{}' user='{}' password='{}' host='{}'" \
        .format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST)
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    while True:
        main()
        print ('----- going to sleep --------------------------------------------------')
        time.sleep(60)

    cur.close()
    conn.close()
