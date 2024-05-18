import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)

clients = []

def broadcast(message, sender_socket):
    for client_socket, name in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                client_socket.close()
                clients.remove((client_socket, name))

def handle_client(client_socket):
    try:
        name = client_socket.recv(1024).decode('utf-8')
        clients.append((client_socket, name))

        welcome_message = f"{name} has joined the chat!"
        print(welcome_message)
        broadcast(welcome_message, client_socket)

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    formatted_message = f"{name}: {message}"
                    broadcast(formatted_message, client_socket)
                else:
                    raise Exception("Empty message received, client may have disconnected.")
            except Exception as e:
                print(f"Error handling client message: {e}")
                client_socket.close()
                clients.remove((client_socket, name))
                broadcast(f"{name} has left the chat.", client_socket)
                break
    except Exception as e:
        print(f"Error in handle_client: {e}")
        client_socket.close()
        if (client_socket, name) in clients:
            clients.remove((client_socket, name))

while True:
    try:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    except Exception as e:
        print(f"Error accepting connections: {e}")