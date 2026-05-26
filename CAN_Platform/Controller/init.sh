#!/bin/bash

cd /home/goncalo/Desktop/Data-Analysis-and-Acquisition-of-Distributed-Vehicular-Systems/CAN_Platform/Controller || exit

# Criar venv apenas se não existir
if [ ! -d "venv" ]; then
    echo "A criar virtualenv..."
    python3 -m venv venv

    source venv/bin/activate

    pip install --upgrade pip

    pip install \
        pyqtgraph \
        pyserial \
        cantools \
        python-can \
        PyQt5

    echo "Setup completo!"
else
    source venv/bin/activate
fi

python main.py