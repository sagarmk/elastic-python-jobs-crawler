#!/bin/bash

LATEST_VERSION=$(curl -Ls https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | awk -F: '{ print $2 }' | tr -d '", ')
wget https://github.com/mozilla/geckodriver/releases/download/${LATEST_VERSION}/geckodriver-${LATEST_VERSION}-linux64.tar.gz
tar -xvzf geckodriver-${LATEST_VERSION}-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver
rm geckodriver-${LATEST_VERSION}-linux64.tar.gz
echo 'export PATH=$PATH:/usr/local/bin/geckodriver' >> ~/.bashrc
source ~/.bashrc
