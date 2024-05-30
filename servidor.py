#!/usr/bin/python

import socket
import time
from collections import deque
from _thread import *
from utils import *

MOTD = '''SOCKER IRC SERVER v0.1 \n by rafael'''

class Cliente:

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.nick = None


    def receber_dados(self):
        try:
            data = decode(self.conn)
            print_receive(data)

            return data
        except error:
            print(error)
            return False

    def enviar_mensagem(self, msg):
        try:
            print_send(msg)
            self.conn.sendall(msg.encode())
        except error:
            print(error)
            self.conn.close()

    def enviar_mensagem_geral(self, msg):
        try:
            self.conn.sendall(msg.encode())
        except error:
            print(error)
            self.conn.close()

    def enviar_pong(self, payload):
        self.enviar_mensagem(f"PONG :{payload}\r\n")


class Servidor:
    def __init__(self,host='localhost',  port=6667, debug=False):
        '''
        Sempre que precisar de uma estrutura de dados que poderá ser acessada em diferentes conexões,
        utilize apenas deque ou queue. Exemplo, para armazenar as conexões ativas:
        '''
        self.conns = deque()
        self.port = port
        self.debug = debug
        self.host = 'localhost'
        self.clientes = []
        self.nicks = {}


    def run(self, conn, addr):
        cliente = Cliente(conn, addr)

        while True:
            dados = cliente.receber_dados()
            while '\r\n' in dados:
                line, dados = dados.split('\r\n', 1)
                if line:
                    self.processar_comando(cliente, line)

    def processar_comando(self, cliente, dados):
        if dados.startswith('NICK'):
            self.processar_nick(cliente, dados.split()[1])
        elif dados.startswith('USER'):
            self.processar_user(cliente, dados.split()[1], dados.split(':')[1])

    def processar_nick(self, cliente, nick):
        if not validate_nick(nick):
            cliente.enviar_mensagem(f"432 * {nick} :Erroneous Nickname\r\n")
        elif nick.lower() in self.nicks:
            cliente.enviar_mensagem(f"433 * {nick} :Nickname is already in use\r\n")
        else:
            if cliente.nick:
                del self.nicks[cliente.nick.lower()]
                mensagem = f":{cliente.nick} NICK {nick}\r\n"
                self.broadcast(mensagem)
                cliente.nick = nick
            else:
                cliente.enviar_mensagem(f"001 {nick} :Welcome to the Internet Relay Network {nick}\r\n")
                cliente.nick = nick
                self.enviar_motd(cliente)

            self.nicks[nick.lower()] = cliente

    def enviar_motd(self, cliente):
        cliente.enviar_mensagem(f"375 {cliente.nick} : {self.host} - Message of the Day -\r\n")
        for line in MOTD.split('\n'):
            cliente.enviar_mensagem(f"372 {cliente.nick} :- {line}\r\n")

        cliente.enviar_mensagem(f"376 {cliente.nick} :End of /MOTD command.\r\n")

    def processar_user(self, cliente, username, realname):
        cliente.username = username
        cliente.realname = realname

    def processar_ping(self, cliente, payload):
        cliente.enviar_pong(payload)

    def broadcast(self, mensagem):
        print_send(mensagem)
        for cliente in self.clientes:
            cliente.enviar_mensagem_geral(mensagem)

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
            print(f"\033[1m\033[94m SOCKET IRC SERVER \n\n Servidor aceitando conexões na porta {self.port}...\n\033[0m")
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
            print("\033[1m\033[94m Servidor Funcionando...\n\033[0m")

def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':
    main()
