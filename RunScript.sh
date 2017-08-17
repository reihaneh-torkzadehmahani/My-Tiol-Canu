#!/bin/bash
clear
echo "Start Installing Dependencies ..."
sudo apt-get update 
echo "Update ..."
sudo apt-get install -y build-essential 
sudo apt-get install -y python-pip 


echo "Installing Toil  ..."
sudo pip install toil

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
sudo rm -r ./src/pipelines/canu/Defaults.pm
sudo cp -r ./src/pipelines/plScripts/Defaults.pm ./src/pipelines/canu
cd ./src
sudo make -j4
cd ../..
sudo cp -r ./src/pipelines/plScripts/*.pl ./Linux-amd64/bin
sudo cp -r ./src/pipelines/plScripts/ToilCanu.py ./Linux-amd64/bin
cd ./Linux-amd64/bin
