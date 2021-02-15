#!/usr/bin/env bash
date >> /home/ignaz/logs/user/cryptobot-restart.log

. /home/ignaz/cryptobot/.env

/home/ignaz/bin/supervisorctl restart cryptobot_fetch_prices >> /home/ignaz/logs/user/cryptobot-restart.log 2>&1
/home/ignaz/bin/supervisorctl restart cryptobot_trader >> /home/ignaz/logs/user/cryptobot-restart.log 2>&1
