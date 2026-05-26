rm -rf venv

python3 -m venv venv --system-site-packages

source venv/bin/activate

pip install pyserial 

echo "Setup completo!"

python test_nextion.py
