#!/bin/sh

echo"========="
echo"Welcome to the bash setup"
echo"========="

if[-d ".env"];
then
     echo "Enabling venv"
else
     echo "No venv"
     exit N
    fi

# Activating the venv

. .env/bin/activate
export ENV=development
python main.py
deactivate 
