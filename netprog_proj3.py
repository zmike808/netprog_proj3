import socket
import threading
import socketserver
import sys
connectedUsers = dict()
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        ip,port =  self.client_address
        clientKey = str(ip) + ":" + str(port)
        #print(clientKey)
        whoami = ""
        while True:
            try:
                data = self.request.recv(65565)
                if not data:
                    continue
                if clientKey in connectedUsers:
                    #print("somehow we made it guys!")
                    data = str(data,'ascii')
                    #print(data)
                    #exit()
                
                    messageBody = data.split("\n")
                    message = messageBody[0].split(" ")
                    #print(message)
                    #break
                    if message[0] == "SEND":
                        #print(message)
                        for key,value in connectedUsers.items():
                            #print("KEY & VALUE:",key,value)
                            
                            if (message[2].lower()).strip("\n") == value:
                                tosend = "FROM " + message[1] + "\n"
                                spliced = messageBody[1:]
                                #print(spliced)
                                for part in spliced:
                                    #print(part)
                                    part = part.strip() + "\n" #readd the \n

                                    #print(part)
                                    #print("part0: ",part[0],"clientKey:",clientKey)
                                    if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                        #print("owow filter worked?")
                                        continue
                                    else:
                                        tosend = tosend + part
                                        #print(part)
                                    

                                #print(tosend)
                                sendtoIP,sendtoPort = key.split(":")
                                #sendtoAddress = sendtoIP,sendtoPort
                                #print ((sendtoIP,int(sendtoPort)))
                                self.request.sendto(bytes(tosend,'ascii'),(sendtoIP,int(sendtoPort)))
                                #self.request.send(bytes("SUCCESS\n",'ascii'))
                                break
                    elif message[0] == "BROADCAST":
                       for key,value in connectedUsers.items():
                           
                            if whoami != value:
                                tosend = "FROM " + whoami + "\n"
                                spliced = messageBody[1:]
                                #print(spliced)
                                for part in spliced:
                                    #print(part)
                                    part = part.strip() + "\n" #readd the \n

                                    #print(part)
                                    #print("part0: ",part[0],"clientKey:",clientKey)
                                    if (part[0] == "C" and part[len(part)-1] == "\n") or (len(part) <= 3 and part[len(part)-1] == "\n" and part[0].isdigit()):
                                        #print("owow filter worked?")
                                        continue
                                    else:
                                        tosend = tosend + part
                                        #print(part)
                                    

                                #print(tosend)
                                sendtoIP,sendtoPort = key.split(":")
                                #sendtoAddress = sendtoIP,sendtoPort
                                #print ((sendtoIP,int(sendtoPort)))
                                self.request.sendto(bytes(tosend,'ascii'),(sendtoIP,int(sendtoPort)))
                    elif message[0] == "LOGOUT":
                        #literally 0 documentation or explaination for this in the project assignment, G plz stahppp
                        for key,value in connectedUsers.items():
                            if value == whoami:
                                del connectedUsers[key]
                                return
                    elif message[0] == "WHO" and message[1] == "HERE":
                        whohere = ""
                        for key,value in connectedUsers.items():
                            whohere = whowhere + value + "\n"
                        
                        self.request.sendall(whohere)
                else:
                    data = str(data,'ascii')
                    data = data.strip("\n")
                    message = data.split(" ")
                    if len(message) == 3 and message[0] == "ME" and message[1] == "IS":
                        #proper login/auth message!
                        if message[2].lower() in connectedUsers.values():
                            response = bytes("ERROR\n", 'ascii')
                            self.request.sendall(response)
                        else:
                            connectedUsers[clientKey] = message[2].lower()
                            whoami = message[2].lower()
                            response = bytes("OK\n", 'ascii')
                            self.request.sendall(response)
                    else:
                        response = bytes("ERROR\n", 'ascii')
                        self.request.sendall(response)
            except:
                pass
       

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
#not part of the project, just some blackmagic i was trying to conjure so i could test 2 clients at 1 time in 1 instance of python, alas python's black magic is just not that strong
class ThreadedClient(threading.Thread):
    def __init__(self,ip, port, message,id):
        super(ThreadedClient,self).__init__()
        self.ip = ip
        self.port=port
        self.message=message
        self.id=id
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        try:
            sock.sendall(bytes(self.message, 'ascii'))
            response = str(sock.recv(1024), 'ascii')
            print("Received: {}".format(response), "client id first response:",self.id)
            if self.id == 2:
                sendTest = "SEND test test2\n C108\n  step off my turf!\n  step off my turf!\n  step off my turf!\n  step off my turf!\n  step off my turf!\n  step off my turf!\n  C8\n  got it?!\n  C0\n"
                sock.sendall(bytes(sendTest,'ascii'))
                response2 = str(sock.recv(1024),'ascii')
                print("THREADEDreceived:",response2)
            else:
                print("waiting to recieve")
                response = str(sock.recv(1024), 'ascii')
                print("Received: {}".format(response),"client id:",self.id)
        finally:
            #pass
            sock.close()
client1 = None
#see threadedclient explaination
def client(ip,port,message,id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("NONTHREADED CLIENT!!!Received: {}".format(response))
        print("waiting to recieve from test\n")
        client1.start()
        #client1.join()
        print("done waiting for join?")
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response),"client id:",id)
    finally:
        #pass
        sock.close()
if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.allow_reuse_address = True

    ip, port = server.server_address
    
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True

    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    #threading.Thread(target=ThreadedClient,args=(ip, port, "ME IS test2",1)

    client1 = ThreadedClient(ip, port, "ME IS test",2)
    #client1.start()
    #lient1.join()
    client(ip,port,"ME IS test2",1)
    #client1.start()
    
    #client(ip, port, "Hello World 3",3)

    server.shutdown()