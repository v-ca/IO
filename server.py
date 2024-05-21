########################################
########################################
##                                    ##
##    Package Installation Section    ##
##                                    ##
########################################
########################################


import os
import sys
import subprocess
import socket
import threading
from typing import Optional

def install_and_import(package: str, import_name: Optional[str] = None) -> None:
    """
    Installs and imports a package.

    Args:
        package: The name of the package to install.
        import_name: The name to use when importing the package. Defaults to the package name.
    """
    import_name = import_name or package
    try:
        __import__(import_name)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            __import__(import_name)
        except Exception as e:
            print(f"Error installing package {package}: {e}")
            raise

def check_and_install_packages() -> None:
    """
    Checks and installs required packages.
    """
    packages = {
        'googletrans': 'googletrans==4.0.0-rc1',
        'cryptography': 'cryptography',
        'torch': 'torch',
        'numpy': 'numpy',
        'transformers': 'transformers'
    }

    for module_name, package_name in packages.items():
        install_and_import(package_name, module_name)

check_and_install_packages()

from cryptography.fernet import Fernet
import torch
import torch.nn as nn
import numpy as np
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from torch.utils.data import Dataset, DataLoader


########################################
########################################
##                                    ##
##    Device Configuration Section    ##
##                                    ##
########################################
########################################


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


##############################################
##############################################
##                                          ##
##    Toxicity Detection Functionality      ##
##                                          ##
##############################################
##############################################


class ToxicCommentsDataset(Dataset):
    """Custom dataset for loading toxic comment data."""

    def __init__(self, texts: list, tokenizer: RobertaTokenizer, max_len: int):
        """
        Initialize the dataset with texts and configuration.

        Args:
            texts (list): List of text strings to be processed.
            tokenizer (RobertaTokenizer): Tokenizer to use for encoding texts.
            max_len (int): Maximum length of encoded tokens.
        """
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self) -> int:
        """Returns the number of items in the dataset."""
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict:
        """Retrieve an item by index."""
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

def is_toxic(message: str, threshold: float = 0.5) -> bool:
    """
    Determine if a message is toxic using a predefined model.

    Args:
        message (str): Message to analyze.
        threshold (float): Probability threshold to consider a message toxic.

    Returns:
        bool: True if the message is considered toxic, False otherwise.
    """
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


##########################################
##########################################
##                                      ##
##    Client Handling Functionality     ##
##                                      ##
##########################################
##########################################


clients = []
key = Fernet.generate_key()
cipher = Fernet(key)

def broadcast(message: str, sender_socket: socket.socket) -> None:
    """
    Broadcast a message to all clients except the sender.

    Args:
        message (str): Message to be broadcasted.
        sender_socket (socket.socket): Socket of the sender to exclude from receiving the message.
    """
    for client_socket, name in clients:
        if client_socket != sender_socket:
            try:
                encrypted_message = cipher.encrypt(message.encode('utf-8'))
                client_socket.send(encrypted_message)
            except Exception as e:
                print(f"Error broadcasting message to {name}: {e}")
                client_socket.close()
                clients.remove((client_socket, name))

def handle_client(client_socket: socket.socket) -> None:
    """
    Handle incoming messages from a client, check for toxicity, and respond accordingly.

    Args:
        client_socket (socket.socket): Client socket to handle communications with.
    """
    try:
        # Send the encryption key to the client
        client_socket.send(key)

        name = client_socket.recv(1024).decode('utf-8')
        if not name:
            raise ValueError("Client did not send a name.")

        print(f"{name} has connected.")

        clients.append((client_socket, name))
        broadcast(f"{name} has joined the chat!", client_socket)

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
                raise ConnectionError("Empty message received, client may have disconnected.")
    except ValueError as e:
        print(f"Error with client {name}: {e}")
    except ConnectionError as e:
        print(f"{name} has disconnected unexpectedly.")
    except Exception as e:
        print(f"Error handling client {name}: {e}")
    finally:
        client_socket.close()
        if (client_socket, name) in clients:
            clients.remove((client_socket, name))
        broadcast(f"{name} has left the chat.", client_socket)


##############################################
##############################################
##                                          ##
##    Server Configuration and Main Loop    ##
##                                          ##
##############################################
##############################################


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(60)

print("Server has started")
print(f"Encryption key: {key.decode()}")
while True:
    try:
        client_socket, addr = server.accept()
        print(f"Connection attempt from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    except Exception as e:
        print(f"Error accepting connections: {e}")
