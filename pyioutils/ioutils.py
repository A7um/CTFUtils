import subprocess 
import threading, sys, os
import socket
import struct
import binascii
import base64

version = 1.2
'''
this is a self defined class as a simple pwntool replacement
when there is not intalled pwntool 
'''

def _to_bytes(data,encoding = "latin-1"):
    if sys.version_info.major==3 and type(data)==str :
        print("BytesWarning: Text is not bytes; assuming ASCII, no guarantees.")
        data = data.encode(encoding)
    return data

def u64(data):
    data = _to_bytes(data)
    return struct.unpack("<Q",data)[0]

def u32(data):
    data = _to_bytes(data)
    return struct.unpack("<I",data)[0]

def u16(data):
    data = _to_bytes(data)
    return struct.unpack("<H",data)[0]

def p64(data):
    return struct.pack("<Q",data)

def p32(data):
    return struct.pack("<I",data)

def p16(data):
    return struct.pack("<H",data)

def u64l(data):
    data = _to_bytes(data)
    return struct.unpack(">Q",data)[0]

def u32l(data):
    data = _to_bytes(data)
    return struct.unpack(">I",data)[0]

def u16l(data):
    data = _to_bytes(data)
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

    def sendline(self, data):
        data = _to_bytes(data)
        return self.sock.send(data+b"\n")
 
    def send(self, data):
        data = _to_bytes(data)
        return self.sock.send(data)
     
    def recv(self, count):
        return self.sock.recv(count)

    def recvuntil(self, delims):
        buf = b''
        while delims not in buf:
            buf += self.recv(1)
        return buf
 
    def recvline(self):
        return self.recvuntil(b"\n")
 
    def recvline_startswith(self, delims):
        buf = b''
        while b'\n' + delims not in buf:
            buf += self.recv(1)
         
        while True:
            tmp = self.recv(1)
            buf += tmp
            if buf == b'\n':
                break
        return buf
    def close(self):
        self.sock.close()

    def interactive(self):
        print ('Switching to interative mode')
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                    if sys.version_info.major==3:
                        sys.stdout.buffer.write(cur)
                    else:
                        sys.stdout.write(cur)
                    sys.stdout.flush()
                except EOFError:
                    print ('Got EOF while reading in interactive')
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()
        while self.sock:
            print ('$ '),
            while True:
                if sys.version_info.major==3:
                    data = sys.stdin.buffer.read(1)
                else:
                    data = sys.stdin.read(1)
                self.send(data)
                if data == b'\n':
                    break

class remote(socket_io):
    def __init__(self, ip, port):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip,port))
        
    
class process:

    def __init__(self, cmd):
        self.pipe = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE)

    def sendline(self, data):
        data = _to_bytes(data)
        return self.pipe.stdin.write(data + b'\n')
 
    def send(self, data):
        data = _to_bytes(data)
        return self.pipe.stdin.write(data)
     
    def recv(self, count):
        return self.pipe.stdout.read(count)
 
    def recvline(self):
        return self.pipe.stdout.readline()
 
    def recvuntil(self, delims):
        buf = b''
        while delims not in buf:
            buf += self.recv(1)
        return buf

    def recvline_startswith(self, delims):
        buf = b''
        while b'\n' + delims not in buf:
            buf += self.recv(1)
         
        while True:
            tmp = self.recv(1)
            buf += tmp
            if buf == b'\n':
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
                    print ('Got EOF while reading in interactive')
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()

    def interactive(self):
        print ('Switching to interative mode')
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                    if sys.version_info.major==3:
                        sys.stdout.buffer.write(cur)
                    else:
                        sys.stdout.write(cur)                    
                    sys.stdout.flush()
                except EOFError:
                    print ('Got EOF while reading in interactive')
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()
        while self.pipe:
            print ('$ '),
            while True:
                if sys.version_info.major==3:
                    data = sys.stdin.buffer.read(1)
                else:
                    data = sys.stdin.read(1)
                self.send(data)
                if data == b'\n':
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
