#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import socket

class Cliente(Exception):
    def __init__(self):
        # Propriedades do cliente
        self.conectado = False

        # Exceção para alarme de tempo (não alterar esta linha)
        signal.signal(signal.SIGALRM, self.exception_handler)

    # Tratamento de exceção para alarme de tempo (não alterar este método)
    def exception_handler(self, signum, frame):
        raise 'EXCEÇÃO (timeout)'

    def receber_dados(self):
        pass

    def executar(self):
        cmd = ''
        print('Cliente!')

        while True:
            '''
            Espera a entrada de um comando por 20 segundos, caso contrário, se uma exceção de tempo
            for disparada, deve-se verificar se há mensagens do servidor para serem lidas e tratadas
            (exemplo: verificar a chegada de ping)
            '''
            signal.alarm(20)
            try:
                cmd = input()
            except Exception as e:
                # Nada foi digitado em 30 segundos, o que fazer?
                # (Exemplo: verificar se há mensagens oriundas do servidor)
                print(e)
                continue
            signal.alarm(0)

            # Um comando foi digitado. Tratar!
            # ...

def main():
    c = Cliente()
    c.executar()


if __name__ == '__main__':
    main()
