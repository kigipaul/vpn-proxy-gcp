#!/bin/bash
if [ ! -e "!CLIENT_CONFIG!" ]; then
    echo "No such file: !CLIENT_CONFIG!"
    exit 1
fi
sudo su -
cd /root
git clone https://github.com/kigipaul/vpn-proxy-ovpn.git vpn-proxy
cp -r !CLIENT_CONFIG! vpn-proxy/config/remote
./vpn-proxy/install.sh

