'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network
import link
import threading
from time import sleep
import sys
INF = 9999999

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 20 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads

    # create network hosts
    host_1 = network.Host(1)
    object_L.append(host_1)
    host_2 = network.Host(2)
    object_L.append(host_2)
    host_3 = network.Host(2)
    object_L.append(host_3)

    # create routers and routing tables for connected clients (subnets)
    router_a_mpls_tbl = {-1: [0, 10, 2], -2: [1, 20, 3]} # This table is confusing as there would not be MPLS frames on the incoming packets. I'm not sure what the keys should be
    router_a = network.Router(name='A',
                              intf_cost_L=[1, 1, 1, 1],
                              intf_capacity_L=[500,500,500,500],
                              mpls_table=router_a_mpls_tbl,
                              max_queue_size=router_queue_size)
    object_L.append(router_a)
    router_b_mpls_tbl = {10: [0,15,1]} #In Label: 10 with attributes in the form [in Interface, out Label, out Interface]
    router_b = network.Router(name='B',
                              intf_cost_L=[1, 2],
                              intf_capacity_L=[500,500],
                              mpls_table=router_b_mpls_tbl,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)
    router_c_mpls_tbl = {20: [0,25,1]}
    router_c = network.Router(name='C',
                              intf_cost_L=[1, 1],
                              intf_capacity_L=[500,500],
                              mpls_table=router_c_mpls_tbl,
                              max_queue_size=router_queue_size)
    object_L.append(router_c)
    router_d_mpls_tbl = {15: [1,"POP",0], 25: [2,"POP",0]} # Whenever POP is seen, pop the MPLS frame from the network packet
    router_d = network.Router(name='D',
                              intf_cost_L=[1, 1, 2],
                              intf_capacity_L=[100,500,500],
                              mpls_table=router_d_mpls_tbl,
                              max_queue_size=router_queue_size)
    object_L.append(router_d)
    # create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    # add all the links
    # host_1
    link_layer.add_link(link.Link(host_1, 0, router_a, 0))

    # host_2
    link_layer.add_link(link.Link(host_2, 0, router_a, 1))

    # host3
    link_layer.add_link(link.Link(host_3, 0, router_d, 0))

    # router_a
    link_layer.add_link(link.Link(router_a, 2, router_b, 0))
    link_layer.add_link(link.Link(router_a, 3, router_c, 0))

    # router_b
    link_layer.add_link(link.Link(router_b, 1, router_d, 1))

    # router_c
    link_layer.add_link(link.Link(router_c, 1, router_d, 2))
    
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    # for i in range(5):
    #     priority = i%2
    #     print(priority)
    #     client.udt_send(2, 'Sample client data %d' % i, priority)
    priority = 0
    host_1.udt_send(3,'Sample client data from host 1 to 3 %d', priority)
    priority = 1
    host_2.udt_send(3,'Sample client data from host 2 to 3 %d', priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #print the final routing tables
    for obj in object_L:
        if str(type(obj)) == "<class 'network.Router'>":
            obj.print_routes()
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically