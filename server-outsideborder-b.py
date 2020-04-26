import logging
import select
import socket
import struct
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import ipfilter

logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass


class SocksProxy(StreamRequestHandler):

    def add(self,bytestring,c):
        tmparray=bytearray(bytestring)
        for i in range(len(tmparray)):
            tmp=tmparray[i]+c
            if tmp>255:
                tmp=tmp-256
            tmparray[i]=tmp
        tmpbytes=bytes(tmparray)
        return tmpbytes
    
    def minus(self,bytestring,c):
        tmparray=bytearray(bytestring)
        for i in range(len(tmparray)):
            tmp=tmparray[i]-c
            if tmp<0:
                tmp=tmp+256
            tmparray[i]=tmp
        tmpbytes=bytes(tmparray)
        return tmpbytes    

    def handle(self):
        logging.info('Accepting connection from %s:%s' % self.client_address)
        if not ipfilter.ipfilter(self.client_address[0]):
            self.server.close_request(self.request)
            logging.info('ipfilter return false %s:%s' % self.client_address)
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect(('127.0.0.1', 9011))
        self.exchange_loop(self.connection, remote)

        self.server.close_request(self.request)
  

    def exchange_loop(self, client, remote):

        while True:

            # wait until client or remote is available for read
            r, w, e = select.select([client, remote], [], [])

            if client in r:
                data = client.recv(4096)
                data = self.minus(data,5)
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                data = self.add(data,5)
                if client.send(data) <= 0:
                    break


if __name__ == '__main__':
    with ThreadingTCPServer(('0.0.0.0', 9010), SocksProxy) as server:
        server.serve_forever()
