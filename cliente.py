import socket
import threading
import time

class Cliente:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.nickname = "nick_padrao"
        self.log_file = "irc_log.txt"

    def connect(self, server_ip, server_port=6667, nickname=None):
        if nickname:
            self.nickname = nickname
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((server_ip, server_port))
            self.connected = True
            print(f"Conectado ao servidor em {server_ip} na porta {server_port}")
            self.send(f"NICK {self.nickname}\r\n")
            self.send(f"USER {self.nickname} 0 * :{self.nickname}\r\n")
            threading.Thread(target=self.receive_messages).start()
        except Exception as e:
            print("Erro ao conectar:", e)
            self.connected = False

    def send(self, msg):
        try:
            self.sock.sendall(msg.encode('utf-8'))
            self.log_message(f"Enviado: {msg}")
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
            self.connected = False

    def receive(self):
        try:
            response = self.sock.recv(4096).decode('utf-8')
            return response
        except Exception as e:
            print("Erro ao receber mensagem:", e)
            self.connected = False
            return ""

    def receive_messages(self):
        while self.connected:
            message = self.receive()
            if message:
                print("Recebido:", message)
                self.log_message(f"Recebido: {message}")

    def close(self):
        self.sock.close()
        self.connected = False
        print("Conexão encerrada")

    def handle_command(self, command):
        parts = command.split(' ', 3) 
        cmd = parts[0]

        if cmd == "/connect":
            if len(parts) > 1:
                server_ip = parts[1]
                server_port = 6667
                nickname = None
                if len(parts) > 2:
                    try:
                        server_port = int(parts[2])
                    except ValueError:
                        print("Porta inválida. Usando porta padrão 6667.")
                if len(parts) > 3:
                    nickname = parts[3]
                self.connect(server_ip, server_port, nickname)
            else:
                print("Uso: /connect <server_ip> [port] [nickname]")
        elif cmd == "/disconnect":
            self.send("QUIT :desconectar\r\n")
            self.close()
        elif cmd == "/join":
            if len(parts) > 1:
                channel = parts[1]
                self.send(f"JOIN {channel}\r\n")
            else:
                print("Uso: /join <#channel>")
        elif cmd == "/leave":
            if len(parts) > 1:
                channel = parts[1]
                self.send(f"PART {channel}\r\n")
            else:
                print("Uso: /leave <#channel>")
        elif cmd == "/msg":
            if len(parts) > 2:
                target = parts[1]
                message = parts[2]
                self.send(f"PRIVMSG {target} :{message}\r\n")
            else:
                print("Uso: /msg <#channel|username> <mensagem>")
        elif cmd == "/names":
            if len(parts) > 1:
                channel = parts[1]
                self.send(f"NAMES {channel}\r\n")
            else:
                print("Uso: /names <#channel>")
        elif cmd == "/privmsg":
            if len(parts) > 2:
                user = parts[1]
                message = parts[2]
                self.send(f"PRIVMSG {user} :{message}\r\n")
            else:
                print("Uso: /privmsg <usuário> <mensagem>")
        elif cmd == "/quit":
            self.send("QUIT :sair\r\n")
            self.close()
        elif cmd == "/help":
            print("/connect <server_ip> [port] [nickname]\n/disconnect\n/join <#channel>\n/leave <#channel>\n/msg <#channel|username> <mensagem>\n/names <#channel>\n/privmsg <user> <mensagem>\n/quit\n/help")
        else:
            print("Comando não reconhecido. Use /help para ver a lista de comandos.")

    def log_message(self, message):
        with open(self.log_file, 'a') as f:
            f.write(message + '\n')

if __name__ == "__main__":
    cliente = Cliente()
    while True:
        command = input("Digite um comando: ")
        cliente.handle_command(command)
        if not cliente.connected:
            break
