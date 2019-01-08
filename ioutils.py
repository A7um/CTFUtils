import subprocess 
import threading, sys, os
import socket
import struct
import binascii
import base64

version = 1.1
'''
this is a self defined class as a simple pwntool replacement
when there is not intalled pwntool 
'''
def u64(data):
    return struct.unpack("<Q",data)[0]

def u32(data):
    return struct.unpack("<I",data)[0]

def u16(data):
    return struct.unpack("<H",data)[0]

def p64(data):
    return struct.pack("<Q",data)

def p32(data):
    return struct.pack("<I",data)

def p16(data):
    return struct.pack("<H",data)

def u64l(data):
    return struct.unpack(">Q",data)[0]

def u32l(data):
    return struct.unpack(">I",data)[0]

def u16l(data):
    return struct.unpack(">H",data)[0]

def p64l(data):
    return struct.pack(">Q",data)

def p32l(data):
    return struct.pack(">I",data)

def p16l(data):
    return struct.pack(">H",data)

def b64e(data):
    return base64.b64encode(data)

def b64d(data):
    return base64.b64decode(data)

def a2h(data):
    return binascii.hexlify(data)

def h2a(data):
    return binascii.unhexlify(data)

class socket_io(object):
    def sendline(self, delims):
        return self.sock.send(delims + '\n')
 
    def send(self, delims):
        return self.sock.send(delims)
     
    def recv(self, count):
        return self.sock.recv(count)

    def recvuntil(self, delims):
        buf = ''
        while delims not in buf:
            buf += self.recv(1)
        return buf
 
    def recvline(self):
        return self.recvuntil("\n")
 
    def recvline_startswith(self, delims):
        buf = ''
        while '\n' + delims not in buf:
            buf += self.recv(1)
         
        while True:
            tmp = self.recv(1)
            buf += tmp
            if buf == '\n':
                break
        return buf
    def close(self):
        self.sock.close()

    def interactive(self):
        print 'Switching to interative mode'
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                    sys.stdout.write(cur)
                    sys.stdout.flush()
                except EOFError:
                    print 'Got EOF while reading in interactive'
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()
        while self.sock:
            print '$ ',
            while True:
                data = sys.stdin.read(1)
                self.send(data)
                if data == '\n':
                    break

class remote(socket_io):
    def __init__(self, ip, port):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip,port))
        
    
class process:
    def __init__(self, cmd):
        self.pipe = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    def sendline(self, delims):
        return self.pipe.stdin.write(delims + '\n')
 
    def send(self, delims):
        return self.pipe.stdin.write(delims)
     
    def recv(self, count):
        return self.pipe.stdout.read(count)
 
    def recvline(self):
        return self.pipe.stdout.readline()
 
    def recvuntil(self, delims):
        buf = ''
        while delims not in buf:
            buf += self.recv(1)
        return buf

    def recvline_startswith(self, delims):
        buf = ''
        while '\n' + delims not in buf:
            buf += self.recv(1)
         
        while True:
            tmp = self.recv(1)
            buf += tmp
            if buf == '\n':
                break
        return buf

    def close(self):
        try:
            self.pipe.kill()
        except OSError:
            pass
    def active(self):
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                except EOFError:
                    print 'Got EOF while reading in interactive'
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()

    def interactive(self):
        print 'Switching to interative mode'
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                    sys.stdout.write(cur)
                    sys.stdout.flush()
                except EOFError:
                    print 'Got EOF while reading in interactive'
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()
        while self.pipe:
            print '$ ',
            while True:
                data = sys.stdin.read(1)
                self.send(data)
                if data == '\n':
                    break

class conn(socket_io):
    def __init__(self, sock, addr):
        self.addr=addr
        self.sock=sock
        
class server:
    def __init__(self, ip, port):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip,port))
        self.sock.listen(5)
    
    def get_conn(self):
        sock,addr=self.sock.accept()
        return conn(sock,addr)

