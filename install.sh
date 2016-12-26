#!/bin/bash
echo Starting #%0 & @ECHO OFF & GOTO :windows
#### BASH SCRIPT STARTS HERE ####

# Check for OS name, but can't trust uname -a for arch
OS=`uname`
# Detect architecture by abusing an integer overflow
if ((1<<32)); then
    ARCH=64 # 64-bit architecture
else
    ARCH=32 # 32-bit architecture
fi

# $OS contains OS name, and $ARCH architecture
clear
PYTHON_VERSION="$(python -c 'import sys; print(sys.version_info[:])')"

if [ ${PYTHON_VERSION:1:1} -ne "3" ]; then
    echo "Install python3"
    exit
fi
python -c 'import cx_Freeze;'
if(($? != 0)); then
    echo "Install cx_Freeze?(y,n)"
    read BIN
    if [ "$BIN" = "y" ]; then
        echo "Installing cx_Freeze"
        pip install cx_Freeze
    else
        exit
    fi
fi

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting installation..."
python setup.py build

echo "Creating global link..."
MAIN_FILE="$(python -c 'import os,glob; bin = os.path.abspath(glob.glob("./build/exe.*/main")[0]); print(bin);')"
touch playbook.sh
echo '#!/bin/sh' >> playbook.sh
echo $MAIN_FILE >> playbook.sh
chmod +x playbook.sh
echo "Enter password to allow global access:"
sudo sh -c "mv playbook.sh /usr/local/bin/playbook"
echo "Installation finished."
echo "Start by tiping 'playbook' into the terminal."
echo "Happy choreo building :)"
