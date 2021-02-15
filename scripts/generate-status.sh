#!/usr/bin/env bash
date >> /home/ignaz/logs/user/cryptobot-status-update.log

. /home/ignaz/cryptobot/.env

/home/ignaz/.venvs/cryptobot/bin/python3 /home/ignaz/cryptobot/status.py >> /home/ignaz/logs/user/cryptobot-status-update.log 2>&1
