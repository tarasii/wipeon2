#!/usr/bin/env bash

cd /home/pi/wipeon2

sudo apt-get install supervisor
sudo cp wipeon.conf /etc/supervisor/conf.d/
sudo supervisorctl update