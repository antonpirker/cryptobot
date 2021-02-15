
import datetime

from dateutil import parser
import psycopg2
from socketclusterclient import Socketcluster

import settings


vwap = {
    1: {},
    3: {},
    5: {},
    10: {},
}


def on_connect(socket):
    print('on connect got called')


def on_disconnect(socket):
    print('on disconnect got called')


def on_connection_error(socket, error):
    print('On connect error got called')


def on_set_authentication(socket, token):
    print('Token received ' + token)
    socket.setAuthtoken(token)


def on_authentication(socket, is_authenticated):
    socket.emitack('auth', settings.COINIGY_SOCKET_CREDENTIALS, authentication_ack)


def get_key(exchange_code, primary_currency, secondary_currency, interval, minute):
    key_number = 0
    for x in range(0, 59, interval):
        if x >= minute:
            key_number = x
            break

    key = '{}-{}-{}-{}'.format(exchange_code, primary_currency, secondary_currency, key_number)
    return key


def receive_trade(key, obj):
    time = parser.parse(obj['timestamp'])
    price = float(obj['price'])
    quantity = float(obj['quantity'])

    exchange_code = obj['exchange']
    primary_currency, secondary_currency = obj['label'].split('/')

    intervals = [1, 3, 5, 10]

    for interval in intervals:
        key = get_key(exchange_code, primary_currency, secondary_currency, interval, time.minute)

        old_time = (time - datetime.timedelta(minutes=interval)).replace(second=0, microsecond=0)
        old_minute = old_time.minute
        old_key = get_key(exchange_code, primary_currency, secondary_currency, interval, old_minute)

        # calculate Volume Weighted Average Price (VWAP)
        if key in vwap[interval].keys():
            vwap[interval][key]['sum_qp'] += quantity*price
            vwap[interval][key]['sum_q'] += quantity
            vwap[interval][key]['avg'] = vwap[interval][key]['sum_qp'] / vwap[interval][key]['sum_q']

        else:
            # save old minute values to db:
            if old_key in vwap[interval].keys():
                timestamp = old_time

                if vwap[interval][old_key]['avg'] != 0:
                    price = vwap[interval][old_key]['avg']
                else:
                    # we were not able to calculate a price for the current minute.
                    # so we take the last price from the database,
                    # to always have a price for every minute
                    cur.execute("""SELECT price FROM prices_%(interval)sm
                                   WHERE exchange_code=%(exchange_code)s AND
                                         primary_currency=%(primary_currency)s AND
                                         secondary_currency=%(secondary_currency)s
                                   ORDER BY time DESC LIMIT 1;""", {
                        'interval': interval,
                        'exchange_code': exchange_code,
                        'primary_currency': primary_currency,
                        'secondary_currency': secondary_currency,
                    })
                    rows = cur.fetchall()
                    price = float(rows[0][0])

                cur.execute("""INSERT INTO prices_%(interval)sm(time, exchange_code,
                                                  primary_currency, secondary_currency,
                                                  price)
                               VALUES (%(time)s, %(exchange_code)s,
                                       %(primary_currency)s, %(secondary_currency)s,
                                       %(price)s);""", {
                    'interval': interval,
                    'time': timestamp,
                    'exchange_code': exchange_code,
                    'primary_currency': primary_currency,
                    'secondary_currency': secondary_currency,
                    'price': price,
                })
                conn.commit()

                del vwap[interval][old_key]

            # initialize new minute values
            vwap[interval][key] = {
                'sum_qp': 0,
                'sum_q': 0,
                'avg': 0,
            }


def subscription_ack(channel, error, obj):
    if not error:
        print('Subscribed successfully to channel ' + channel)
        socket.onchannel(channel, receive_trade)


def authentication_ack(eventname, error, obj):
    if not error:
        for market in settings.TRADING_MARKETS:
            trades_channel = 'TRADE-{}--{}--{}'.format(market['exchange_code'],
                                                       market['primary_currency'],
                                                       market['secondary_currency'])
            socket.subscribeack(trades_channel, subscription_ack)


if __name__ == '__main__':
    connection_string = "dbname='{}' user='{}' password='{}' host='{}'"\
        .format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST)
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    socket = Socketcluster.socket(settings.COINIGY_SOCKET_URL)
    socket.setBasicListener(on_connect, on_disconnect, on_connection_error)
    socket.setAuthenticationListener(on_set_authentication, on_authentication)
    socket.connect()
