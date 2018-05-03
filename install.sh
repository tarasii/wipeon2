#!/usr/bin/env bash

cd /home/pi/wipeon2

sudo apt-get update
sudo apt-get install python-pip
sudo pip install --index-url=http://pypi.python.org/simple/ --upgrade pip

pip install -r requirements.txt

sudo apt-get install supervisor
sudo cp wipeon.conf /etc/supervisor/conf.d/
sudo supervisorctl update

sudo apt-get install avahi-daemon
sudo cp wipeon.service /etc/avahi/services/

sudo usermod -a -G lpadmin pi

#python /home/pi/wipeon2/print_barcode.py buttons