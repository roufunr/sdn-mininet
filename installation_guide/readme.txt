Step #1
sudo apt install mininet

Step #2
sudo apt update 
sudo apt upgrade
sudo apt install python3.9 python3.9-venv python3.9-dev

Step #3
python3.9 -m venv venv

Step #4
source venv/bin/activate


Step #4
make mininet systemwide available
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> venv/lib/python3.9/site-packages/mininet.pth


Step #5
pip install -r requirements.txt

Step #6
sudo python test_topo.py