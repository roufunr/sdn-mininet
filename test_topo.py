from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

class MyTopo(Topo):
    def build(self):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host11 = self.addHost('h11')
        host12 = self.addHost('h12')
        host21 = self.addHost('h21')
        host22 = self.addHost('h22')
        self.addLink(host11, switch1)
        self.addLink(host12, switch1)
        self.addLink(host21, switch2)
        self.addLink(host22, switch2)
        self.addLink(switch1, switch2)

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=MyTopo())
    net.start()
    CLI(net)
    net.stop()
