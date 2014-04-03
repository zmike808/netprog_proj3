# First the server

#!/usr/bin/env python
#!/usr/bin/env python

"""
A basic, multiclient 'chat server' using Python's select module
with interrupt handling.

Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys
import signal
sendHistory = []
BUFSIZE = 1024

totalMessages = 0
class ChatServer(object):
    """ Simple chat server using select """
    
    def __init__(self, port=3490, backlog=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.usernames = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print 'Listening to port',port,'...'
        self.server.listen(backlog)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        # Close the server
        print 'Shutting down server...'
        # Close existing client sockets
        for o in self.outputs:
            o.close()
            
        self.server.close()

    def getname(self, client):

        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))
        
    def serve(self):
        
        inputs = [self.server,sys.stdin]
        self.outputs = []

        running = 1

        while running:

            try:
                inputready,outputready,exceptready = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            except socket.error, e:
                break

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'chatserver: got connection %d from %s' % (client.fileno(), address)
                    # Read the login name
                    #try:
                    cname = client.recv(BUFSIZE)#.split('ME IS ')[1].strip("\n").lower()
                    split = cname.split(" ")
                    if split[0] == "ME" and split[1] == "IS" and len(split) == 3:
                        cname = split[2].strip("\n")
                        cname = cname.lower()
                    else:
                        client.sendall("ERROR\n")
                        #print cname
                    #except:
                        #cname = ""
                    if cname == "":
                        client.sendall("ERROR\n")
                        continue
                    
                    if cname in self.usernames:
                        client.sendall("ERROR\n")
                        continue
                    else:
                        self.usernames[cname] = client #keep track of usernames paired to the client id
                        print "cname is: ", cname
                        client.sendall("OK\n")
                    
                    # Compute client name and send back
                    self.clients += 1
                    #send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)

                    self.clientmap[client] = (address, cname)
                    
                    
                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0
                else:
                    # handle all other sockets
                    try:
                        # data = s.recv(BUFSIZ)
                        data = s.recv
                        
                        if data:
                            # Send as new client's message...
                            messageBody = data.split("\n")
                            message = messageBody[0].split(" ")
                            if message[0] == "SEND":
                                tosend = "FROM " + message[1] + "\n"
                                
                                    
                                sendHistory.append(message[1])
                                
                                spliced = messageBody[1:]
                                for part in spliced:
                                    #print(part)
                                    part = part.strip() + "\n" #readd the \n
                                    for x in range(2,len(message)):
                                        self.usernames[message[x]].sendall(part)
                                    #print(part)
                                    #print("part0: ",part[0],"clientKey:",clientKey)
                                    #if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                        #print("owow filter worked?")
                                        #continue
                                    #else:
                                        #tosend = tosend + part
                                
                                #if len(sendHistory) == 3:
                                    
                            elif message[0] == "BROADCAST":
                                tosend = "FROM " + message[1] + "\n"
                                spliced = messageBody[1:]
                                for part in spliced:
                                    #print(part)
                                    part = part.strip() + "\n" #readd the \n
                                    for key in self.usernames:
                                        self.usernames[key].send(part)
                                    #print(part)
                                    #print("part0: ",part[0],"clientKey:",clientKey)
                                    #if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                        #print("owow filter worked?")
                                        #continue
                                    #else:
                                        #tosend = tosend + part
                                
                            elif message[0] == "WHO" and message[1] == "HERE":
                                whohere = ""
                                for key in self.usernames:
                                    whohere = whowhere + key + "\n"
                                self.usernames[message[2]].send(whohere)
                            elif message[0] == "LOGOUT":
                                self.clients -= 1
                                del self.usernames[message[1]]
                                s.close()
                                inputs.remove(s)
                                self.outputs.remove(s)
                               
                        else:
                            #print 'chatserver: %d hung up' % s.fileno()
                            self.clients -= 1
                            for key,value in usernames:
                                if value == s:
                                    del usernames[key]
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)
                            
                                    
                            
                                
                    except socket.error, e:
                        # Remove
                        for key,value in usernames:
                                if value == s:
                                    del usernames[key]
                        inputs.remove(s)
                        self.outputs.remove(s)
                        


        self.server.close()

if __name__ == "__main__":
    ChatServer().serve()