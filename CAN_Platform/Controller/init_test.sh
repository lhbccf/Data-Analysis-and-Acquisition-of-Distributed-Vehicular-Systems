rm -rf venv

python3 -m venv venv --system-site-packages

source venv/bin/activate

pip install pyqtgraph
pip install pyserial 
pip install cantools

echo "Setup completo!"

python test_can.py
