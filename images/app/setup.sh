#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y mysql-client libdbd-mysql-perl libmysqlclient-dev libmysqlclient16 libmysqlclient16-dev mysql-client memcached apache2 apache2-mpm-worker libapache2-mod-wsgi git-core mercurial curl python-setuptools djbdns python-virtualenv python-mysqldb python-imaging python-dev

cd /tmp/
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python get-pip.py

sudo mkdir -p /var/www/playdation.net/playdation
sudo chown ubuntu:ubuntu -R /var/www/playdation.net


cd /var/www/playdation.net/playdation

git init .
git remote add playip git@184.73.230.35:/home/git/
git pull playip
git checkout -b local playip/dev


virtualenv /var/www/playdation.net/env

source /var/www/playdation.net/env/bin/activate

pip install -r /var/www/playdation.net/playdation/requirements/base.txt


sudo cp apache_conf/playdation.net  /etc/apache2/sites-enabled/
sudo rm /etc/apache2/sites-enabled/000-default
sudo ln -s /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
sudo /etc/init.d/apache2 restart

cp  /var/www/playdation.net/playdation/images/app/local_settings.py /var/www/playdation.net/playdation/
python manage.py build_static

