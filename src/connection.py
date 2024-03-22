import socket
import threading
import time

class Connection:

    def __init__(self, host, address, port, debug = False):
        
        self.alive = True
        self.host, self.address, self.port  = host, address, port
        self.last_message = ""
        self.connected = False
        self.debug = debug
        threading.Thread(target = self.connect, name="Socket trying to connect", daemon=True).start()
    
    def connect(self):
        if self.host:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.setblocking(0)
            try :
                self.server.bind(("0.0.0.0", self.port))
                self.server.listen()
            except :
                return
            address = None
            while self.alive:
                try :
                    self.conn, (address, _) = self.server.accept()
                    if address != self.address:
                        self.conn.close()
                        self.conn = None
                    else :
                        if self.debug:
                            print(f"Connected with {address}")
                            print("----------------")
                        break
                except BlockingIOError:
                    time.sleep(0.5)
                except OSError:
                    time.sleep(0.5)
            self.server.close()
        else :
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            redo = True
            while redo and self.alive:
                try :
                    redo = False
                    self.conn.connect((self.address, self.port))
                    if self.debug:
                        print(f"Connected with {self.address}")
                        print("----------------")
                except ConnectionRefusedError:
                    redo = True
                    time.sleep(0.5)
                except OSError:
                    time.sleep(0.5)
        
        if self.alive:
            self.conn.setblocking(1)
            self.connected = True
            threading.Thread(target=self.listening, name="Listening to socket", daemon=True).start()

    def listening(self):
        while self.alive:
            try :
                self.last_message = self.conn.recv(1024).decode("utf-8")
                if self.last_message == "":
                    raise Exception()
                if self.debug:
                    print(f"[CONNECTION] >> {self.last_message}")
            except :
                if self.debug:
                    print("----------------")
                    print("Connection Lost")
                self.connected = False
                break

            if self.last_message == "!close":
                self.close()
                return

        if self.alive:
            self.connect()

    def send(self, message):
        if self.connected:
            try :
                self.conn.send(message.encode("utf-8"))
                if self.debug:
                    print(f"[CONNECTION] << {message}")
            except ConnectionResetError:
                if self.debug:
                    print(f"[DEBUG] error sending message {message}")
            except OSError:
                if self.debug:
                    print(f"[DEBUG] error sending message {message}")

    def close(self):
        """Close all the sockets and ports used, don't tell the other part"""

        self.alive = False
        self.connected = False

        if hasattr(self, "conn"):
            if self.conn != None:
                self.conn.close()

        if hasattr(self, "server"):
            if self.server != None:
                self.server.close()
        
        if self.debug:
            print("[DEBUG] connection closed cleanly")

        del self

    def end_connection(self, message = "!close", wait = True):
        """Send a message expressly telling the other part to close the connection and then close it itself
        Allow to close cleanly the connection from the both part"""
        last = 0
        while self.connected:
            if time.time() - last > 5:
                self.send(message)
                last = time.time()
            if not wait:
                break
            time.sleep(0.5)
        self.close()

class GroupConnection:

    def __init__(self, mcast_group = ("239.1.2.3", 55555), debug = False):

        self.active = True
        self.last_message = None
        self.debug = debug

        self.mcast_group = mcast_group

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.mcast_group[0]) + socket.inet_aton('0.0.0.0'))
        self.sock.bind(("", self.mcast_group[1]))
        self.sock.setblocking(0)

        threading.Thread(target=self.group_listen, name="Listening to multicast socket", daemon=True).start()

    def group_send(self, message):
        if self.active:
            self.sock.sendto(message.encode("utf-8"), self.mcast_group)

    def group_listen(self):
        while self.active:
            try :
                message, addr = self.sock.recvfrom(1024)
                message = message.decode("utf-8")
                self.last_message = (message, addr)
                if self.debug:
                    print(f"[GROUP]({addr[0]}:{addr[1]}) : {message}")
            except :
                time.sleep(0.1)

    def close(self):
        self.active = False
        self.sock.close()