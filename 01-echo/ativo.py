import socket

HOST = 'localhost'
PORTA = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((HOST, PORTA))

loop = True
while loop:
    user_in = input('> ')
    if user_in == 'fim':
        loop = False
    else:
        user_in += '\n'
        sock.send(user_in.encode('utf-8'))
        msg = sock.recv(1024)
        print(msg.decode('utf-8'), end='')

sock.close()
