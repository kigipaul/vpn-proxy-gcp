#!/bin/bash
sudo su -
cd /root
git clone https://github.com/kigipaul/vpn-proxy-ovpn.git vpn-proxy
cp -r !CLIENT_CONFIG! vpn-proxy/config/remote
./vpn-proxy/install.sh

