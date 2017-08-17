#!/bin/bash
clear
echo "Start Installing Dependencies ..."
sudo apt-get update > /dev/null 2>&1
echo "Update ..."
sudo apt-get install -y build-essential > /dev/null 2>&1
echo "Build ..."
sudo apt-get install -y python-pip > /dev/null 2>&1
echo "Pip ..."

echo "Installing Toil  ..."
pip install toil

echo "Installing java8  ..."
sudo apt-get install software-properties-common> /dev/null 2>&1
sudo add-apt-repository ppa:webupd8team/java -y > /dev/null 2>&1
echo "Update ..."
sudo apt-get update > /dev/null 2>&1
echo "Installer ..."
sudo apt-get install -y oracle-java8-installer
echo "......."
sudo apt-get install -y oracle-java8-set-default > /dev/null

echo "Installing gnuplot  ..."
sudo apt-get install -y gnuplot > /dev/null 2>&1
sudo apt-get update> /dev/null 2>&1

echo "Installing canu  ..."
sudo git clone https://github.com/marbl/canu.git
sudo rm -r /home/ubuntu/canu/src/pipelines/canu/Defaults.pm
sudo cp -r /home/ubuntu/canu/src/pipelines/canu/ReihanehScripts/Defaults.pm /home/ubuntu/canu/src/pipelines/canu
cd canu/src
make
cd /home/ubuntu/canu/Linux-amd64/bin
sudo cp -r /home/ubuntu/canu/src/pipelines/canu/ReihanehScripts/*.pl /home/ubuntu/canu/Linux-amd64/bin
sudo cp -r /home/ubuntu/ForGit/ToilCanu.py /home/ubuntu/canu/Linux-amd64/bin
