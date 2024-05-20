import socket
import threading

from cryptography.fernet import Fernet
import os
import torch
import torch.nn as nn
import numpy as np
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from torch.utils.data import Dataset, DataLoader


if torch.cuda.is_available():
    device = torch.device('cuda')
    print("Using CUDA")
elif torch.backends.mps.is_available():
    device = torch.device('mps')
    print("Using Apple Metal (MPS)")
else:
    device = torch.device('cpu')
    print("Using CPU")


tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=6)
model.load_state_dict(torch.load('best_model.pth', map_location=device))
model.to(device)
model.eval()


class ToxicCommentsDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        inputs = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        input_ids = inputs['input_ids'].squeeze()
        attention_mask = inputs['attention_mask'].squeeze()
        return {'input_ids': input_ids, 'attention_mask': attention_mask}


# Function to check if a message is toxic
def is_toxic(message, threshold=0.5):
    dataset = ToxicCommentsDataset([message], tokenizer, max_len=256)
    loader = DataLoader(dataset, batch_size=1, shuffle=False)

    with torch.no_grad():
        for batch in loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.sigmoid(logits).cpu().numpy()

    # Consider message toxic if any class probability is above the threshold
    return np.any(probabilities > threshold)


# Modify your server code to integrate the toxic message filtering
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if is_toxic(message):
                response = "Your message was flagged as inappropriate and will not be sent."
            else:
                response = message
                # Broadcast the message to other clients or process it as needed

            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling message: {e}")
            client_socket.close()
            break

# Generate a key for encryption
key = Fernet.generate_key()
cipher = Fernet(key)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)

clients = []

def broadcast(message, sender_socket):
    for client_socket, name in clients:
        if client_socket != sender_socket:
            try:
                encrypted_message = cipher.encrypt(message.encode('utf-8'))
                client_socket.send(encrypted_message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                client_socket.close()
                clients.remove((client_socket, name))


def handle_client(client_socket):
    name = client_socket.recv(1024).decode('utf-8')
    clients.append((client_socket, name))
    broadcast(f"{name} has joined the chat!", client_socket)

    try:
        while True:
            encrypted_message = client_socket.recv(1024)
            if encrypted_message:
                message = cipher.decrypt(encrypted_message).decode('utf-8')

                if is_toxic(message):
                    client_socket.send(cipher.encrypt("Your message was flagged as inappropriate.".encode('utf-8')))
                else:
                    formatted_message = f"{name}: {message}"
                    broadcast(formatted_message, client_socket)
            else:
                raise Exception("Empty message received, client may have disconnected.")
    except Exception as e:
        print(f"Error handling client message: {e}")
        client_socket.close()
        clients.remove((client_socket, name))
        broadcast(f"{name} has left the chat.", client_socket)


print("Server has started")
print(f"Encryption key: {key.decode()}")
while True:
    try:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    except Exception as e:
        print(f"Error accepting connections: {e}")