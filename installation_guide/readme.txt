Step #1
sudo apt install mininet

Step #2
sudo apt update 
sudo apt upgrade
sudo apt install python3.10 python3.10-venv python3.10-dev

Step #3
python3.10 -m venv ryu-venv

Step #4
source ryu-venv/bin/activate


Step #4
make mininet systemwide available
deactivate  # Exit the virtual environment
source ryu-venv/bin/activate  # Reactivate it

# Allow access to system-wide packages
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> ryu-venv/lib/python3.10/site-packages/mininet.pth

Step #5
pip install -r requirements.txt