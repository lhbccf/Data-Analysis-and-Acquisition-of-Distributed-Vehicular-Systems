
cd ~/Desktop/Data-Analysis-and-Acquisition-of-Distributed-Vehicular-Systems/CAN_Platform/Controller/UI

rm -rf venv

python3 -m venv venv --system-site-packages

source venv/bin/activate

pip install pyqtgraph

echo "Setup completo!"

python test.py
