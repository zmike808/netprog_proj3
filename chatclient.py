#############################################################################
# The chat client
#############################################################################
#! /usr/bin/env python

"""
Simple chat client for the chat server. Defines
a simple protocol to be used with chatserver.

"""

import socket
import sys
import select

BUFSIZE = 8192

class ChatClient(object):
    """ A simple command line chat client using select """

    def __init__(self, name, host='198.23.178.34', port=3490):
        self.name = name
        # Quit flag
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
        self.prompt='[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print 'Connected to chat server@%d' % self.port
            # Send my name...
            self.sock.sendall("ME IS " + self.name + "\n") 
            data = self.sock.recv(BUFSIZE)
            print data
            if(data != "OK\n"):
                print "DATA MISMATCH?????",data
            while True:
                #self.sock.sendall("BROADCAST test\nC10\n") 
                input = sys.stdin.readline().strip()
                #print input
                tosend = ""
                while input != "ENDNOW":
                    tosend = tosend + input + "\n"
                    input = sys.stdin.readline().strip()
                    
                print "SENDING TO SERVER:"
                print tosend
                self.sock.sendall(tosend)
                reply = self.sock.recv(BUFSIZE)
                print "RECEIVED FROM SERVER:"
                print reply
            # Contains client address, set it
            #addr = data.split('CLIENT: ')[1]
            #self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
        except socket.error, e:
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def cmdloop(self):

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])
                
                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline()
                        if data: 
                            #print "before sendall", data
                            #testmessage = "WHO HERE test"#"BROADCAST test\ntesting\nomgplswork\n"
                            self.sock.sendall(data)
                    elif i == self.sock:
                        data = self.sock.recv(BUFSIZE)
                        if not data:
                            print 'Shutting down.'
                            self.flag = True
                            break
                        else:
                            #print "data in else/write??", data
                            sys.stdout.write(data)
                            sys.stdout.flush()
                            
            except KeyboardInterrupt:
                print 'Interrupted.'
                self.sock.close()
                break
            
            
if __name__ == "__main__":
    import sys

    if len(sys.argv)<3:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])
        
    client = ChatClient(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    #client.cmdloop()

