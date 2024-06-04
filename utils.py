import re

def print_receive(str):
    print(f"\033[96m>>> {str}\033[0m")

def print_send(str):
    print(f"\033[95m<<< {str}\033[0m")

def print_error(str):
    print(f"\033[91m{str}\033[0m")

def decode(conn):
    return conn.recv(512).decode().strip()

def validar_nick(nick):
    if len(nick) > 9:
        return False

    if not nick[0].isalpha():
        return False

    if not re.match("^[A-Za-z0-9_]*$", nick):
        return False

    return True

def validar_nome_canal(nome_canal):
    if not nome_canal:
        return False

    if len(nome_canal) > 63:
        return False

    if not nome_canal.startswith("#"):
        return False

    if not re.match("^#[A-Za-z0-9_]*$", nome_canal):
        return False

    return True
