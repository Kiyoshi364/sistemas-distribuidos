import socket

HOST = ''
PORTA = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((HOST, PORTA))

sock.listen(5)

print("Pronto para receber conexoes...")

novoSock, endereco = sock.accept()
print ('Conectado com: ', endereco)

while True:
    msg = novoSock.recv(1024)
    if not msg:
        break
    else:
        print(msg.decode('utf-8'), end='')
        novoSock.send(msg)

novoSock.close()

sock.close()
