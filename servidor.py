#!/usr/bin/python

import socket
import time
from collections import deque
from _thread import *

MOTD = '''SOCKER IRC SERVER v0.1'''

class Cliente:
    
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.buffer = ""
        self.nome = None


    def receber_dados(self):
        try:
            data = self.conn.recv(1024).decode('utf-8')
            if not data:
                return False
            self.buffer += data
            while '\r\n' in self.buffer:
                line, self.buffer = self.buffer.split('\r\n', 1)
                self.processar_comando(line)
            return True
        except error:
            print(error)
            return False
        
    def processar_comando(self, line):
        print(f"Recebido de {self.addr}: {line}")
        if line.startswith("NICK"):
            self.nome = line.split(':')[1]
            self.enviar_dados(f":{self.nome} NICK recebido\r\n")
        elif line.startswith("QUIT"):
            self.enviar_dados(f"Desconectando: {self.nome}\r\n")
            self.conn.close()

    def enviar_dados(self, msg):
        try:
            self.conn.sendall(msg.encode('utf-8'))
        except error:
            print(error)
            self.conn.close()

class Servidor:
    def __init__(self,host='localhost',  port=6667, debug=False):
        '''
        Sempre que precisar de uma estrutura de dados que poderá ser acessada em diferentes conexões,
        utilize apenas deque ou queue. Exemplo, para armazenar as conexões ativas:
        '''
        self.conns = deque()
        self.port = port
        self.debug = False
        self.host = host


    def run(self, conn, addr):
        cliente = Cliente(conn, addr)
        conn.send(MOTD.encode())
        self.conns.append(cliente)
        while cliente.receber_dados():
            pass
        self.conns.remove(cliente)
        pass


    def listen(self):
        '''
        NÃO ALTERAR
        Escuta múltiplas conexões na porta definida, chamando o método run para
        cada uma. Propriedades da classe Servidor são vistas e podem
        ser alteradas por todas as conexões.
        '''
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind(('', self.port))
        _socket.listen(4096)
        while True:
            print(f'Servidor aceitando conexões na porta {self.port}...')
            client, addr = _socket.accept()
            start_new_thread(self.run, (client, addr))

    def start(self):
        '''
        NÃO ALTERAR
        Inicia o servidor no método listen e fica em loop infinito.
        '''
        start_new_thread(self.listen, ())

        while True:
            time.sleep(60)
            print('Servidor funcionando...')
            
    def message_of_the_day(self, msg):
        print(f'MOTD: {msg}')
        


def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':
    main()
