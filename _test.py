#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:01:37 2020
​
@author: apple
"""
from Util import Agent
import socketserver 
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.
​
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        #print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        command = eval(self.data)
        # just send back the same data, but upper-cased
        if command['type'] == 'open':
            print('try to open a store')            
            ID, message = self.server.Agent.open_store((command['Location']['X'],command['Location']['Y']), command['Menu'], command['Inventory'])
            self.request.sendall(bytes(str({'store_ID':ID, 'type': message}), "utf-8"))
        if command['type'] == 'close':
            print('tyr_to_close_store')
            ID, message = self.server.Agent.close_store(command['store_ID'])
            print(ID)
            self.request.sendall(bytes(str({'store_ID': ID, 'type': message}), "utf-8"))
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    Agent1 = Agent()
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT),  MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.Agent = Agent1
        server.serve_forever()            
#Agent1 = Agent()           
'''if command['type'] == 'open':
    print('try to open a store')
    Agent1.open_store((command['Location']['X'],command['Location']['Y']), command['Menu'], command['Inventory'])
elif command['type'] == 'close':
    print('try to open a store')
    Agent1.close_store()'''