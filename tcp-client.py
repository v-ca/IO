import socket
import threading

name = input('Enter your name: ')
if name == 'admin':
    password = input('Enter your password: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.tcp.ngrok.io', 10958))

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NAME':
                client.send(name.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASSWORD':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'Incorrect Password':
                        print('Password is incorrect. Please try again.')
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused: BANHAMMER 3000.')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print('An error occurred!')
            client.close()
            break

def send():
    while True:
        if stop_thread:
            break
        message = f'{name}: {input("")}'
        if message[len(name)+2:].startswith('/'): # /kick username -> KICK username
            if name == 'admin':
                if message[len(name)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(name)+2+6:]}'.encode('utf-8'))
                elif message[len(name)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(name)+2+5:]}'.encode('utf-8'))
                elif message[len(name)+2:].startswith('/shutdown'):
                    client.send('SHUTDOWN'.encode('utf-8'))
            else:
                print("I'm sorry. I can not do that dave.")
        else:
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()