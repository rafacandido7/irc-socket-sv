#!/usr/bin/python

import socket
import time
from collections import deque
from _thread import *

MOTD = '''SOCKER IRC SERVER v0.1'''

class Cliente:
    def __init__(self, conn):
        self.conn = conn

    def receber_dados(self):
        pass

    def enviar_dados(self, msg):
        pass

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


    def run(self, conn):
        Cliente(conn)
        self.conns.append(conn)
        # send MODT msg
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
            start_new_thread(self.run, (client, ))

    def start(self):
        '''
        NÃO ALTERAR
        Inicia o servidor no método listen e fica em loop infinito.
        '''
        start_new_thread(self.listen, ())

        while True:
            time.sleep(60)
            print('Servidor funcionando...')


def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':
    main()
