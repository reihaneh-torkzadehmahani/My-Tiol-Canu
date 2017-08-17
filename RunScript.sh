#!/bin/bash
clear
echo "Start Installing Dependencies ..."
sudo apt-get update 
echo "Update ..."
sudo apt-get install -y build-essential 
sudo apt-get install -y python-pip 


echo "Installing Toil  ..."
pip install toil

echo "Installing java8  ..."
sudo apt-get install software-properties-common 
sudo add-apt-repository ppa:webupd8team/java -y 
sudo apt-get update 
sudo apt-get install -y oracle-java8-installer
sudo apt-get install -y oracle-java8-set-default 

echo "Installing gnuplot  ..."
sudo apt-get install -y gnuplot 
sudo apt-get update

echo "Installing canu  ..."
sudo git clone https://github.com/marbl/canu.git
sudo rm -r ./src/pipelines/canu/Defaults.pm
sudo cp -r ./src/pipelines/canu/plScripts/Defaults.pm ./src/pipelines/canu
cd canu/src
sudo make
cd ./Linux-amd64/bin
sudo cp -r ./src/pipelines/canu/plScripts/*.pl ./Linux-amd64/bin
sudo cp -r ./src/pipelines/canu/plScripts/ToilCanu.py ./Linux-amd64/bin
