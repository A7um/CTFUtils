import subprocess 
import threading, sys, os
import socket
'''
this is a self defined class as a simple pwntool replacement
when there is not intalled pwntool 
'''

class remote:
    def __init__(self, ip, port):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip,port))
        
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
                
class process:
    def __init__(self, cmd):
        self.pipe = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE,  shell = True)
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


