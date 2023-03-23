#!/bin/sh

# Log the time the cron job is run
echo "Running cron job at `date`" >> /app/cron.log

# Run the python script
python3 -m flask --app rail_rank save-ppm-data
python3 -m flask --app rail_rank prune-data
