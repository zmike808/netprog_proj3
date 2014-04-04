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
from collections import defaultdict
import signal
import random
sendHistory = dict()
verbose = False
BUFSIZE = 8192
randomMessages = ["Hey, you're kinda hot","No way!","I like Justin Bieber....a lot","yo","dawg","wutt","inda","bawt","GGWP","python2good","plznerf","pythonSOEZ","GODBLESS-NO_CSTRINGS_EZMODE"]
totalMessages = 0
class ChatServer(object):
    """ Simple chat server using select """
    
    def __init__(self, port=(sys.argv[1:]), backlog=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.usernames = dict()
        self.serverList = []
        self.sendHistory = defaultdict(list)
        if len(port) < 1:
            print sys.argv
            exit()
        for p in port:
            p = int(p)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('',p))
            print 'Listening to port',p,'...'
            server.listen(backlog)
            self.serverList.append(server)
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
        
        inputs = self.serverList#[self.server,sys.stdin]
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

                if s in self.serverList:
                    if s.type == socket.DGRAM:
                        #addrInfo = socket.getnameinfo(s)
                        pass
                    else:
                        # handle the server socket
                        client, address = s.accept()
                        print 'chatserver: got connection %d from %s' % (client.fileno(), address)
                        # Read the login name
                        try:
                            cname = client.recv(BUFSIZE)#.split('ME IS ')[1].strip("\n").lower()
                            split = cname.split(" ")
                            if split[0] == "ME" and split[1] == "IS" and len(split) == 3:
                                cname = split[2].strip("\n")
                                cname = cname.lower()
                            else:
                                client.sendall("ERROR\n")
                                break
                                #print cname
                        except:
                            break
                                              
                        
                        if cname in self.usernames:
                            client.sendall("ERROR\n")
                            break
                        else:
                            self.usernames[cname] = client #keep track of usernames paired to the client id
                            #print "cname is: ", cname
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
                        if s.type == socket.DGRAM:
                        else:
                            data = s.recv(BUFSIZE)
                            #data = s.recv
                            print data
                            
                            if data:
                                # Send as new client's message...
                                messageBody = data.split("\n")
                                message = messageBody[0].split(" ")
                                #print "split with spaces",message
                                #print "split by \\n",messageBody
                                if message[0] == "SEND":
                                    tosend = "FROM " + message[1] + "\n"                       
                                    spliced = messageBody[1:]
                                    if verbose:
                                        print "RCVD from",message[1],"(",message[1].gethostname(),"):"
                                        for msg in messageBody:
                                            print msg
                                    wholeMsg = ""
                                    for part in spliced:
                                        #print(part)
                                        part = part.strip() + "\n" #readd the \n
                                        wholeMsg = wholeMsg + part
                                        for x in range(2,len(message)):
                                            self.usernames[message[x]].sendall(part)
                                            self.sendHistory[message[x]].append(message[1])
                                            if len(self.sendHistory[message[x]]) == 3:
                                                rMessage = randomMessage[random.randint(0,12)]
                                                rFrom = (self.sendHistory[message[x]])[random.randint(0,2)]
                                                msgSent = "FROM "+rFrom+"\n"+len(rMessage)+"\n"+rMessage
                                                if verbose:
                                                    print "SENT (randomly!) TO",+message[x],"(",message[x].gethostname(),"):"
                                                    print msgSent
                                                self.usernames[message[x]].sendall(msgSent)
                                                self.sendHistory[message[x]] = []
                                        #print(part)
                                        #print("part0: ",part[0],"clientKey:",clientKey)
                                        #if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                            #print("owow filter worked?")
                                            #continue
                                        #else:
                                            #tosend = tosend + part
                                    if verbose:
                                        for x in range(2,len(message)):
                                            print "SENT to",message[x],"(",message[x].gethostname(),"):"
                                            print wholeMsg
                                elif message[0] == "BROADCAST":
                                    tosend = "FROM " + message[1] + "\n"
                                    spliced = messageBody[1:]
                                    wholeMsg = ""
                                    for part in spliced:
                                        #print(part)
                                        part = part.strip() + "\n" #readd the \n
                                        print part
                                        wholeMsg = wholeMsg + part
                                        for key in self.usernames:
                                            self.usernames[key].send(part)
                                            self.sendHistory[key].append(message[1])
                                            if len(self.sendHistory[key]) == 3:
                                                rMessage = randomMessage[random.randint(0,12)]
                                                rFrom = (self.sendHistory[key])[random.randint(0,2)]
                                                msgSent = msgSent = "FROM "+rFrom+"\n"+len(rMessage)+"\n"+rMessage
                                                if verbose:
                                                    print "SENT (randomly!) TO",+message[x],"(",message[x].gethostname(),"):"
                                                    print msgSent
                                                self.usernames[key].sendall(msgSent)
                                                self.sendHistory[key] = []
                                        #print(part)
                                        #print("part0: ",part[0],"clientKey:",clientKey)
                                        #if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                            #print("owow filter worked?")
                                            #continue
                                        #else:
                                            #tosend = tosend + part
                                    if verbose:
                                        for key in self.usernames:
                                            print "SENT to",message[x],"(",message[x].gethostname(),"):"
                                            print wholeMsg
                                elif message[0] == "WHO" and message[1] == "HERE":
                                    whohere = ""
                                    
                                    for key in self.usernames:
                                        whohere = whowhere + key + "\n"
                                    self.usernames[message[2]].send(whohere)
                                    if verbose:
                                        print "RCVD from",message[2],"(",message[2].gethostname(),"):"
                                        print whohere
                                elif message[0] == "LOGOUT":
                                    self.clients -= 1
                                    del self.usernames[message[1]]
                                    s.close()
                                    inputs.remove(s)
                                    self.outputs.remove(s)
                                        
                            else:
                                #print 'chatserver: %d hung up' % s.fileno()
                                self.clients -= 1
                                for key,value in self.usernames.items():
                                    if value == s:
                                        del self.usernames[key]
                                s.close()
                                inputs.remove(s)
                                self.outputs.remove(s)
                            
                                    
                            
                                
                    except socket.error, e:
                        # Remove
                        for key,value in self.usernames.items():
                                if value == s:
                                    del self.usernames[key]
                        inputs.remove(s)
                        self.outputs.remove(s)
                        


        self.server.close()

if __name__ == "__main__":
    args = sys.argv
    if "-v" in args:
        verbose = True
        args.remove("-v")
    ChatServer().serve()