from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import hub

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mac_to_device = {}  # Store MAC-to-device mapping
        self.prev_mac_to_port = {}  # Track previous state
        self.logger.info("\n[SimpleSwitch13 Initialized]")
        
        # Start logging forwarding table changes periodically
        self.monitor_thread = hub.spawn(self.log_forwarding_table)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.logger.info("\n[Switch Connected] Switch ID: s%s", datapath.id)

        # Install table-miss flow entry (send unknown packets to controller)
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, 
                                          datapath.ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return  # Ignore LLDP packets

        dpid = datapath.id
        src = eth.src
        dst = eth.dst

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_device.setdefault(dpid, {})

        # Identify if MAC belongs to a switch, host, or controller
        device_name = f"h{int(src[-2:], 16) % 10}"  # Rough estimation of hosts
        if src.startswith("ca"):  # Example: If controller has a known prefix
            device_name = "controller"
        elif src in self.mac_to_port[dpid]:
            device_name = f"s{dpid}"

        # Log only if the MAC is newly learned
        if src not in self.mac_to_port[dpid]:
            self.logger.info("\n[LEARNING] Switch s%s learned MAC %s (%s) at port %s", dpid, src, device_name, in_port)

        self.mac_to_port[dpid][src] = in_port
        self.mac_to_device[dpid][src] = device_name

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = datapath.ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != datapath.ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)

    def log_forwarding_table(self):
        """
        Periodically logs only the CHANGES in the forwarding table.
        """
        while True:
            hub.sleep(5)  # Check every 5 seconds
            changes_detected = False

            for dpid, table in self.mac_to_port.items():
                prev_table = self.prev_mac_to_port.get(dpid, {})

                # Identify new or changed entries
                new_entries = {k: v for k, v in table.items() if k not in prev_table or prev_table[k] != v}

                if new_entries:
                    changes_detected = True
                    self.logger.info("\n[FORWARDING TABLE UPDATED] Switch s%s:", dpid)
                    self.logger.info("| MAC Address          | Port | Device       |")
                    self.logger.info("|----------------------|------|--------------|")
                    for mac, port in new_entries.items():
                        device_name = self.mac_to_device[dpid].get(mac, "Unknown")
                        self.logger.info("| %-20s | %-4s | %-12s |", mac, port, device_name)

            # Update the previous state only if there were changes
            if changes_detected:
                self.prev_mac_to_port = {dpid: table.copy() for dpid, table in self.mac_to_port.items()}




# from ryu.base import app_manager
# from ryu.controller import ofp_event
# from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
# from ryu.controller.handler import set_ev_cls
# from ryu.ofproto import ofproto_v1_3
# from ryu.lib.packet import packet, ethernet, ether_types

# class SimpleSwitch13(app_manager.RyuApp):
#     OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

#     def __init__(self, *args, **kwargs):
#         super(SimpleSwitch13, self).__init__(*args, **kwargs)
#         self.mac_to_port = {}

#     @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
#     def switch_features_handler(self, ev):
#         datapath = ev.msg.datapath
#         ofproto = datapath.ofproto
#         parser = datapath.ofproto_parser

#         # Install a table-miss flow entry
#         match = parser.OFPMatch()
#         actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
#         self.add_flow(datapath, 0, match, actions)

#     def add_flow(self, datapath, priority, match, actions, buffer_id=None):
#         ofproto = datapath.ofproto
#         parser = datapath.ofproto_parser
#         inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
#         mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
#         datapath.send_msg(mod)

#     @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
#     def packet_in_handler(self, ev):
#         msg = ev.msg
#         datapath = msg.datapath
#         ofproto = datapath.ofproto
#         parser = datapath.ofproto_parser
#         in_port = msg.match['in_port']

#         pkt = packet.Packet(msg.data)
#         eth = pkt.get_protocol(ethernet.ethernet)

#         if eth.ethertype == ether_types.ETH_TYPE_LLDP:
#             return  # Ignore LLDP packets

#         dst = eth.dst
#         src = eth.src

#         dpid = datapath.id
#         self.mac_to_port.setdefault(dpid, {})

#         self.mac_to_port[dpid][src] = in_port

#         if dst in self.mac_to_port[dpid]:
#             out_port = self.mac_to_port[dpid][dst]
#         else:
#             out_port = ofproto.OFPP_FLOOD

#         actions = [parser.OFPActionOutput(out_port)]

#         if out_port != ofproto.OFPP_FLOOD:
#             match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
#             self.add_flow(datapath, 1, match, actions)

#         out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
#                                   in_port=in_port, actions=actions, data=msg.data)
#         datapath.send_msg(out)
