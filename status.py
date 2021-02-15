import datetime
import json
import requests
import os

import jinja2
import psycopg2
import psycopg2.extras

import settings

COINIGY_HEADERS = {
    'Content-Type': 'application/json',
    'X-API-KEY': settings.COINIGY_API_KEY,
    'X-API-SECRET': settings.COINIGY_API_SECRET,
}

NUM_TRADES = 10


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


if __name__ == '__main__':
    connection_string = "dbname='{}' user='{}' password='{}' host='{}'"\
        .format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST)
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    context = {
        'now': datetime.datetime.now(datetime.timezone.utc),
    }

    # fetch trades
    cur.execute("""SELECT time, trade_type, exchange_code, 
                          amount, amount_currency, 
                          price, price_currency, 
                          profit
                   FROM trades
                   ORDER BY time DESC LIMIT %(count)s;""", {
        'count': NUM_TRADES,
    })
    rows = cur.fetchall()
    context['trades'] = rows

    # fetch balance
    payload = {
        'exchange_code': 'BTRX',
        'exchange_market': 'BTC/USDT',
    }
    r = requests.post(settings.COINIGY_API_BASE_URL + 'ticker',
                      headers=COINIGY_HEADERS, data=json.dumps(payload))
    data = json.loads(r.content.decode('utf-8'))
    btc_price = (float(data['data'][0]['ask'])+float(data['data'][0]['bid']))/2

    r = requests.post(settings.COINIGY_API_BASE_URL + 'balances',
                      headers=COINIGY_HEADERS)
    data = json.loads(r.content.decode('utf-8'))

    sum_btc = sum([float(balance['btc_balance']) for balance in data['data']])
    context['balance'] = sum_btc*btc_price
    context['balance_currency'] = 'USD'

    # render template
    html = render(os.path.join(settings.TEMPLATES_DIR, 'status.html'), context)
    f = open('/home/ignaz/webapps/ignaz_at/status.html', 'w')
    f.write(html)
    f.close()
