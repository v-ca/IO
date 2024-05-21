# IO Chat

## Overview

IO Chat is a secure, encrypted, and auto-translating chatroom that integrates real-time intelligent systems and natural language processing. This project aims to provide a robust platform for users to communicate across different languages securely. The chat system filters out negative or toxic messages using advanced machine learning techniques to ensure a positive communication environment.

## Features

- **Encryption**: All messages are encrypted using Fernet (symmetric encryption) to ensure that communication is secure and private.
- **Auto-Translation**: Messages can be automatically translated into the user's preferred language, making it easier for people from different linguistic backgrounds to communicate.
- **Real-Time Communication**: Built on sockets for real-time messaging.
- **Toxic Message Filtering**: Integrates a pre-trained machine learning model to detect and filter out toxic messages.
- **Dynamic Language Support**: Supports multiple languages, allowing users to choose their preferred communication language.

## Repository Structure

```plaintext
IO-chat/
│
├── client.py        - Client application for connecting to the chat server.
├── server.py        - Server application that handles incoming connections and messages.
├── requirements.txt - Requirements file that contains all necessary packages.
└── README.md        - Documentation about the project.
```

## Setup Instructions

### Requirements
- Python 3.8 or higher
- Network access (if deploying across multiple machines)

### Prerequisites
Ensure Python 3.8+ is installed on your machine. Additionally, the following packages are required:
- `socket`
- `threading`
- `googletrans==4.0.0-rc1`
- `cryptography`
- `torch`
- `transformers`

### Clone the Repository
Start by cloning the repository to your local machine:
```bash
git clone https://github.com/yourusername/IO-chat.git
cd IO-chat
```

### Install Dependencies
Run the following command to install necessary Python packages:

```bash
pip install -r requirements.txt
```   

### Running the Server
Navigate to the directory containing server.py.
Run the server script:

```bash
python server.py
```

### Running the Client
Navigate to the directory containing client.py.
Run the client script:

```bash 
python client.py
```

### Using Ngrok to Connect Clients Remotely
To connect clients to the server over the internet, you can use Ngrok to expose your local server publicly.

#### Download and Setup Ngrok
Go to [Ngrok](https://ngrok.com/) and sign up if you haven't already.
Follow the setup instructions to download and install Ngrok on your machine.

#### Start Ngrok
Open a terminal and run Ngrok to expose your server port (default is 9999 - make sure this matches the chosen port number in the server.py file) to the internet:

```bash
ngrok tcp 9999
```

### Usage
#### Starting the Server
Execute `server.py` to start the server. The server will listen for incoming connections on the specified port. 

You will also need to either train a RoBERTa model and add the `best_model.pth` file to the repo or request it. Unforunately, the 400+MB file size procludes me from including is in this repo, and it will not successfully upload using GitHub Large File. 

#### Connecting as a Client
- Run `client.py` on the client machine.
- Enter the server's IP or ngrok address and port number when prompted.
- Choose a display name and preferred language for the chat.
- Once connected, type messages into the terminal to chat. Translated messages will be displayed in your chosen language.
Chatting
- Type your message and press Enter to send. The chatroom supports multi-client communication, with messages being encrypted and optionally translated.

## Next Steps
- Implement a GUI for easier interaction.
- Expand the language model to include more dialects and slang for better translation accuracy.
- Optimize encryption for faster performance with larger groups.
- Enhance the toxic message filtering by continuously training the model with new data.
- Add a spellchecker to work with improving the translation accuracy.