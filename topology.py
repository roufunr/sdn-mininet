from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

class MyTopo(Topo):
    def build(self):
        switch0 = self.addSwitch('s0')
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')
        host11 = self.addHost('h11')
        host12 = self.addHost('h12')
        host13 = self.addHost('h13')
        host21 = self.addHost('h21')
        host22 = self.addHost('h22')
        host23 = self.addHost('h33')
        host31 = self.addHost('h31')
        host32 = self.addHost('h32')
        host33 = self.addHost('h33')
        
        # Connecting hosts to switches
        self.addLink(host11, switch1)
        self.addLink(host12, switch1)
        self.addLink(host13, switch1)
        self.addLink(host21, switch2)
        self.addLink(host22, switch2)
        self.addLink(host23, switch2)
        self.addLink(host31, switch3)
        self.addLink(host32, switch3)
        self.addLink(host33, switch3)
        
        #Connecting all switches through switch 0
        self.addLink(switch1, switch0)
        self.addLink(switch2, switch0)
        self.addLink(switch3, switch0)
        

if __name__ == '__main__':
    setLogLevel('info')

    # Connect Mininet to a remote Ryu controller
    net = Mininet(topo=MyTopo(), controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633))

    net.start()
    CLI(net)  # Open Mininet CLI for manual testing
    net.stop()
