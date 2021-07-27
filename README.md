# cryptobot

At the beginning of 2018 I locked myself into a AirBnB for two days to build a Bitcoin trading bot in Python.
At the end of this weekend I had a working trading bot that could buy and sell Bitcoin as well as a simple algorithm based on rolling averages for deciding when to buy/sell.

After a couple of weeks tweaking the algorithm I let the bot trade for 30 days in April 2018 (it did not make any money, ...)

I presented this project at the PyDays Vienna in 2019. Here you see the slides:
[https://slides.com/antonpirker/building-a-bitcoin-trading-bot-in-python](https://slides.com/antonpirker/building-a-bitcoin-trading-bot-in-python)

The presentation was more about how to get something done in a weekend than trading bitcoin.

Currently the bot is defunct because the API I used for trading and getting real time price information of Bitcoin became really expensive to have this bot running.

## Description of the code

This are just a couple of plain python scripts that where run on a cheap server.
The most important parts are:

* `fetch_prices.py` - A script that connects to a websocket to receive realtime Bitcoin trading information. The script saves the data into a Postgres database.
* `trade.py` - The main trading script. It was run once every minute and it decided (base on the data that `fetch_prices.py` saved in the database) if the time was right to buy or sell coins.
* `status.py` - A simple script that just reads from the trading API how many coins I have and what trades where made. It generates a index.html file and puts it somewhere for nginx to serve.

And that's basically it. It is really simple, but it worked great.

## Running the code

I used [supervisor](http://supervisord.org/) to start and keep `fetch_prices.py` and `trade.py` running in case one of the script crashes.
The `trade.py` script basically did an endless loop where it made a trading decision, made a buy/sell and then went to sleep for 60 seconds after wich it woke up and did the same again, and again, and again.
The `fetch_prices.py` script just opens up a websocket connection to a Bitcoin prices API and listens for incoming trades to save them in to the database.
I had a cronjob that killed `fetch_prices.py` every once in a while because the websocket connect hung sometimes.

It worked great. I started it once and it run the test month without a problem.