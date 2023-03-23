#!/bin/sh

# Log the time the cron job is run
echo "Running cron job at `date`" >> /app/cron.log

# Run the python script
python3 -m flask --app train_app save-ppm-data
python3 -m flask --app train_app prune-data
