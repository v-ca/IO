import socket
import threading


host = '127.0.0.1' # localhost
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
names = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('utf-8').startswith('KICK'):
                if names[clients.index(client)] == 'admin':
                    name_to_kick = message.decode('utf-8')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            elif message.decode('utf-8').startswith('BAN'):
                if names[clients.index(client)] == 'admin':
                    name_to_ban = message.decode('utf-8')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} has felt the swift justice of the BANHAMMER!!')
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            elif message.decode('utf-8') == 'SHUTDOWN':
                if names[clients.index(client)] == 'admin':
                    broadcast('Server is shutting down...'.encode('utf-8'))
                    for client in clients:
                        client.close()
                    server.close()
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            else:
                broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                name = names[index]
                broadcast(f'{name} has left the chat'.encode('utf-8'))
                names.remove(name)
                break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NAME'.encode('utf-8'))

        name = client.recv(1024).decode('utf-8')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if name+'\n' in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        if name == 'admin':
            client.send('PASSWORD'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != 'adminpass':
                client.send('Incorrect Password'.encode('utf-8'))
                client.close()
                continue
            else:
                client.send('Welcome admin'.encode('utf-8'))


        names.append(name)
        clients.append(client)

        print(f'Name of the client is {name}')
        broadcast(f'{name} has entered chat\n'.encode('utf-8'))
        client.send('Connected to the server'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in names:
        name_index = names.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were wasted.'.encode('utf-8'))
        client_to_kick.close()
        names.remove(name)
        broadcast(f'{name} was eliminated.'.encode('utf-8'))

print('Server is listening...')
receive()