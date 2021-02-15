import datetime
import json

import requests

import settings

COINIGY_HEADERS = {
    'Content-Type': 'application/json',
    'X-API-KEY': settings.COINIGY_API_KEY,
    'X-API-SECRET': settings.COINIGY_API_SECRET,
}


if __name__ == '__main__':
    # get current bitcoin price
    payload = {
        'exchange_code': 'BTRX',
        'exchange_market': 'BTC/USDT',
    }
    r = requests.post(settings.COINIGY_API_BASE_URL + 'ticker',
                      headers=COINIGY_HEADERS, data=json.dumps(payload))
    data = json.loads(r.content.decode('utf-8'))
    btc_price = (float(data['data'][0]['ask'])+float(data['data'][0]['bid']))/2

    # get balances
    r = requests.post(settings.COINIGY_API_BASE_URL + 'balances',
                      headers=COINIGY_HEADERS)
    data = json.loads(r.content.decode('utf-8'))

    sum_btc = sum([float(balance['btc_balance']) for balance in data['data']])
    print('')
    print('Estimated value: {:.2f} USD'.format(sum_btc*btc_price))

    print('Current balances:')
    balance_list = ''
    for item in data['data']:
        print('- {}: {}'.format(item['balance_curr_code'], float(item['balance_amount_avail'])))
        balance_list = '{}\n        <li>{}: {}</li>'.format(balance_list,
                                                            item['balance_curr_code'],
                                                            float(item['balance_amount_avail']))

    html = """
<html>
<body>
    Estimated value: {:.2f} USD / {:.6f} BTC
    <br/><br/>
    Current balances:
    <ul>{}</ul>
    <br/><br/>
    {}
    </body>
</html>
    """.format(sum_btc*btc_price, sum_btc, balance_list, datetime.datetime.now())

    f = open('/home/ignaz/webapps/ignaz_at/balance.html', 'w')
    f.write(html)
    f.close()
