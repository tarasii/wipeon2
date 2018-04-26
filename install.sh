#!/usr/bin/env bash

cd /home/pi/wipeon2

pip install -r requirements.txt

sudo apt-get install supervisor
sudo cp wipeon.conf /etc/supervisor/conf.d/
sudo supervisorctl update

sudo apt-get install avahi-daemon
sudo cp wipeon.service /etc/avahi/services/

#python /home/pi/wipeon2/print_barcode.py buttons