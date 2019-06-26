# -*- coding: UTF-8 -*-
import socket
import threading
import os
import sys
import base64
import hashlib
import struct
from GlobalWindy import *

# ====== config ======
HOST='localhost'

PORT = 8888

MAGIC_STRING='258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

HANDSHAKE_STRING="HTTP/1.1 101 Switching Protocols\r\n"\
      "Upgrade:websocket\r\n"\
      "Connection: Upgrade\r\n"\
      "Sec-WebSocket-Accept: {1}\r\n"\
      "WebSocket-Location:ws://{2}/chat\r\n"\
      "WebSocket-Protocol:chat\r\n\r\n"
class Th(threading.Thread):
    ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))
    def __init__(self, connection,):
        super(Th, self).__init__()
        self.con = connection


    def run(self):
        while(True):
            data = self.recv_data(4096)
            point = data.split('/')
            start = point[0].split(',')
            destiny = point[1].split(',')
            slat = start[0]; slng = start[1]
            dlat = destiny[0]; dlng = destiny[1]
            if(data):
                str = 'python ' + self.ROOT + '\Main.py' +\
                      ' '+ slat +\
                      ' '+ slng +\
                      ' '+ dlat +\
                      ' '+ dlng
                # execfile(str)
                print str
                os.system(str)
                self.send_data('complete')
        # self.debug('test')

    def debug(self, str):
        print str

    def recv_data(self, num):
        all_data = self.con.recv(num)
        if(len(all_data)):
            code_len=ord(all_data[1]) & 127
            if(code_len ==126):
                masks=all_data[4:8]
                data=all_data[8:]
            elif(code_len ==127):
                masks=all_data[10:14]
                data=all_data[14:]
            else:
                masks=all_data[2:6]
                data=all_data[6:]
            raw_str=""
            i=0
            for d in data:
                raw_str+=chr(ord(d) ^ ord(masks[i%4]))
                i+=1
            return raw_str

    def send_data(self, data):
        if(data):
            data=str(data)
        else:
            return False
        token="\x81"
        length=len(data)
        if(length < 126):
            token+=struct.pack("B", length)
        elif(length <=0xFFFF):
            token+=struct.pack("!BH",126, length)
        else:
            token+=struct.pack("!BQ",127, length)
        #struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        data='%s%s' % (token, data)
        self.con.send(data)
        return True

class Server:

    # handshake
    def recieveSignal(signal):
        pass

    def sendSignal(sell):
        pass

    def handshake(self, con):
        headers={}
        shake=con.recv(1024)
        if not len(shake):
            return False
        header, data =shake.split('\r\n\r\n',1)
        for line in header.split('\r\n')[1:]:
            key, val =line.split(': ',1)
            headers[key]=val
        if'Sec-WebSocket-Key'not in headers:
            print('This socket is not websocket, client close.')
            con.close()
            return False
        sec_key=headers['Sec-WebSocket-Key']
        res_key=base64.b64encode(hashlib.sha1(sec_key +MAGIC_STRING).digest())
        str_handshake=HANDSHAKE_STRING.replace('{1}', res_key).replace(
            '{2}',
            HOST +
            ':' +
            str(PORT)
        )
        print str_handshake
        con.send(str_handshake)
        return True

    def new_service(self):
        """start a service socket and listen
        when coms a connection, start a new thread to handle it"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((HOST,PORT))
            sock.listen(1)
            #链接队列大小
            print"Server bind ", PORT, "ready to use"
        except:
            print("Server is already running,quit")
            sys.exit()
        while(True):
            connection, address = sock.accept()
            #返回元组（socket,add），accept调用时会进入waite状态
            print"Got connection from ", address
            if(self.handshake(connection)):
                print"handshake success"
                try:
                    t=Th(connection)
                    t.start()
                    print'new thread for client ...'
                except:
                    print'start new thread error'
                    connection.close()
    def debug(self, str):
        print str

if(__name__ == '__main__'):
    server = Server()
    server.new_service()