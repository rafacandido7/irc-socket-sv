#!/usr/bin/python

import socket
import time
from collections import deque
from _thread import start_new_thread
from utils import *

MOTD = '''SOCKER IRC SERVER v0.1 \n by rafael'''

class Cliente:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.nick = None
        self.username = None
        self.realname = None
        self.buffer = ""

    def receber_dados(self):
        try:
            data = self.conn.recv(1024).decode()
            if not data:
                return False
            self.buffer += data
            if '\r\n' in self.buffer:
                lines = self.buffer.split('\r\n')
                self.buffer = lines.pop()
                print_receive("\r\n".join(lines) + "\r\n")
                return lines
            return []
        except Exception as e:
            print(e)
            return False

    def enviar_mensagem(self, msg):
        try:
            while len(msg) > 0:
                part = msg[:512]
                print_send(part)
                self.conn.sendall(part.encode())
                msg = msg[512:]
        except Exception as e:
            print(e)
            self.conn.close()

    def enviar_mensagem_geral(self, msg):
        try:
            while len(msg) > 0:
                part = msg[:512]
                print_send(f"GENERAL: {part}")
                self.conn.sendall(part.encode())
                msg = msg[512:]
        except Exception as e:
            print(e)
            self.conn.close()

    def enviar_pong(self, payload):
        self.enviar_mensagem(f"PONG : {payload}\r\n")

class Servidor:
    def __init__(self, host='localhost', port=6667, debug=False):
        self.conns = deque()
        self.port = port
        self.debug = debug
        self.host = host
        self.clientes = []
        self.nicks = {}
        self.canais = {}

    def run(self, conn, addr):
        cliente = Cliente(conn, addr)
        self.clientes.append(cliente)
        try:
            while True:
                linhas = cliente.receber_dados()
                if linhas is False:
                    break
                for dados in linhas:
                    if dados:
                        self.processar_comando(cliente, dados)
        except Exception as e:
            print(e)
        finally:
            self.remover_cliente(cliente)

    def processar_comando(self, cliente, dados):
        partes = dados.split()
        if len(partes) == 0:
            return

        print(f"Partes: {partes}")

        comando = partes[0].upper()

        if comando == 'NICK' and len(partes) > 1:
            self.processar_nick(cliente, partes[1])
        elif comando == 'USER' and len(partes) > 4:
            username = partes[1]
            realname = dados.split(':', 1)[1] if ':' in dados else ''
            self.processar_user(cliente, username, realname)
        elif comando == 'PING' and len(partes) > 1:
            self.processar_ping(cliente, partes[1])
        elif comando == 'JOIN' and len(partes) > 1:
            self.processar_join(cliente, partes[1])
        elif comando == 'PART' and len(partes) > 1:
            canal = partes[1]
            motivo = dados.split(':', 1)[1] if ':' in dados else ''
            self.processar_part(cliente, canal, motivo)
        elif comando == 'WHO' or comando == 'NAMES' and len(partes) > 1:
            self.processar_names(cliente, partes[1])
        elif comando == 'PRIVMSG' and len(partes) > 2:
            self.processar_privmsg(cliente, partes[1], " ".join(partes[2:]))
        elif comando == 'QUIT':
            motivo = dados.split(':', 1)[1] if ':' in dados else ''
            self.processar_quit(cliente, motivo)

    def processar_nick(self, cliente, nick):
        nick = nick.lower()
        if not validar_nick(nick):
            cliente.enviar_mensagem(f"432 * {nick} :Erroneous Nickname\r\n")
        elif nick in self.nicks:
            cliente.enviar_mensagem(f"433 * {nick} :Nickname is already in use\r\n")
        else:
            if cliente.nick:
                del self.nicks[cliente.nick.lower()]
                mensagem = f":{cliente.nick} NICK {nick}\r\n"
                self.broadcast(mensagem, cliente)
            else:
                cliente.enviar_mensagem(f"001 {nick} :Welcome to the Internet Relay Network {nick}\r\n")
                cliente.nick = nick
                self.enviar_motd(cliente)
            cliente.nick = nick
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

    def processar_join(self, cliente, canal):
        valid = validar_nome_canal(canal)
        if not valid:
            cliente.enviar_mensagem(f":{self.host} 403 {cliente.nick} {canal}:No such channel\r\n")
            return

        if canal not in self.canais:
            self.canais[canal] = []

        self.canais[canal].append(cliente.nick)
        cliente.enviar_mensagem(f":{cliente.nick} JOIN :{canal}\r\n")

        for nick in self.canais[canal]:
            if nick != cliente.nick:
                outro_cliente = self.nicks.get(nick, None)
                if outro_cliente:
                    outro_cliente.enviar_mensagem(f":{cliente.nick} JOIN :{canal}\r\n")

    def processar_part(self, cliente, canal, motivo):
        if canal not in self.canais or cliente.nick not in self.canais[canal]:
            cliente.enviar_mensagem(f":{self.host} 442 {cliente.nick} {canal} :You’re not on that channel\r\n")
            return

        self.canais[canal].remove(cliente.nick)
        mensagem = f":{cliente.nick} PART {canal} :{motivo}\r\n"
        self.broadcast(mensagem, None)

        if len(self.canais[canal]) == 0:
            del self.canais[canal]

    def processar_names(self, cliente, canal):
        self.usuarios_no_canal(cliente, canal)

    def processar_quit(self, cliente, motivo):
        mensagem = f":{cliente.nick} QUIT :{motivo}\r\n"
        self.broadcast(mensagem, cliente)
        self.remover_cliente(cliente)

    def processar_privmsg(self, cliente, destino, mensagem):
        destino = destino.lower()
        mensagem = mensagem.strip()

        if destino.startswith('#'):
            if destino in self.canais:
                for nick in self.canais[destino]:
                    outro_cliente = self.nicks.get(nick, None)
                    if outro_cliente and outro_cliente != cliente:
                        outro_cliente.enviar_mensagem(f":{cliente.nick} PRIVMSG {destino} :{mensagem}\r\n")
            else:
                cliente.enviar_mensagem(f":{self.host} 403 {cliente.nick} {destino} :No such channel\r\n")
        else:
            # bonuses hehe :)
            outro_cliente = self.nicks.get(destino, None)
            if outro_cliente:
                outro_cliente.enviar_mensagem(f":{cliente.nick} PRIVMSG {destino} :{mensagem}\r\n")
            else:
                cliente.enviar_mensagem(f":{self.host} 401 {cliente.nick} {destino} :No such nick/channel\r\n")

    def remover_cliente(self, cliente, motivo='Client Quit'):
        if cliente in self.clientes:
            self.clientes.remove(cliente)

        if cliente.nick and cliente.nick.lower() in self.nicks:
            del self.nicks[cliente.nick.lower()]

        for canal in list(self.canais):
            if cliente.nick in self.canais[canal]:
                self.canais[canal].remove(cliente.nick)
                self.broadcast(f":{cliente.nick} PART {canal} :{motivo}\r\n")

                if len(self.canais[canal]) == 0:
                    del self.canais[canal]

        cliente.conn.close()

    def usuarios_no_canal(self, cliente, canal):
        lista_usuarios = ' '.join(self.canais[canal])
        cliente.enviar_mensagem(f":{self.host} 353 {cliente.nick} = {canal} :{lista_usuarios}\r\n")
        cliente.enviar_mensagem(f":{self.host} 366 {cliente.nick} {canal} :End of /NAMES list.\r\n")

    def broadcast(self, mensagem, sender=None):
        print_send(mensagem)
        for cliente in self.clientes:
            if cliente != sender:
                cliente.enviar_mensagem_geral(mensagem)

    def listen(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind(('', self.port))
        _socket.listen(4096)
        while True:
            print(f"\033[1m\033[94mSOCKER IRC SERVER \n\nServidor aceitando conexões na porta {self.port}...\n\033[0m")
            client, addr = _socket.accept()
            start_new_thread(self.run, (client, addr))

    def start(self):
        start_new_thread(self.listen, ())
        while True:
            time.sleep(60)
            print("\033[1m\033[94mServidor Funcionando...\n\033[0m")

def main():
    s = Servidor(host='', port=6667, debug=True)
    s.start()

if __name__ == '__main__':
    main()
