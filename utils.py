import re

def print_receive(str):
    print(f"\033[96m>>> {str}\033[0m")

def print_send(str):
    print(f"\033[95m<<< {str}\033[0m")

def print_error(str):
    print(f"\033[91m{str}\033[0m")

def decode(conn):
    return conn.recv(1024).decode().strip()

def validate_nick(nick):
    if len(nick) > 9:
        return False

    if not nick[0].isalpha():
        return False

    if not re.match("^[A-Za-z0-9_]*$", nick):
        return False

    return True
