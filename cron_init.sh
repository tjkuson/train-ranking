#!/bin/sh

crontab -r

echo "*/30 * * * * /bin/sh /app/cron.sh &> /app/cron.log" >| train_crontab
crontab train_crontab

chmod 777 /app/cron.sh
echo "Setup cron.sh" >| /app/cron.log

echo "Running cron"
cron -f &

echo "Running data collection"
python3 -m rail_rank.data &