# IO Chatroom

**THIS REPO IS A WORK-IN-PROGRESS AND INITIAL COMMIT WAS CREATED TO ADD SERVER AND CLIENT FILES.**

## NEXT STEPS:
- Create a GUI for clients
- Institute NLP and social network graphs for further analysis

## Overview
IO Chatroom is a simple real-time chat application using sockets in Python. It features a server and a client script that enable multiple clients to connect and communicate via a centralized server. The application supports basic chat features, including administrative commands to kick or ban users, and the ability to shut down the server gracefully from an admin client.

## Features
- **Real-time Communication**: Users can send and receive messages instantly.
- **Admin Controls**: Admin users can kick or ban other users and shut down the server.
- **Concurrency**: Multiple users can connect and communicate simultaneously.
- **Connection Management**: Handles user disconnections and maintains a list of connected clients.

## Repository Structure
- `server.py`: Contains all the server-side logic.
- `client.py`: Contains all the client-side logic.
- `bans.txt`: Stores a list of banned user names.

## Setup Instructions

### Requirements
- Python 3.8 or higher
- Network access (if deploying across multiple machines)

### Running the Server
1. Navigate to the directory containing `server.py`.
2. Run the server script:
    ```sh
    python server.py
    ```

### Running the Client
1. Navigate to the directory containing `client.py`.
2. Run the client script:
    ```sh
    python client.py
    ```

### Using Ngrok to Connect Clients Remotely
To connect clients to the server over the internet, you can use Ngrok to expose your local server publicly.

#### Download and Setup Ngrok:
1. Go to [Ngrok](https://ngrok.com/) and sign up if you haven't already.
2. Follow the setup instructions to download and install Ngrok on your machine.

#### Start the Server:
1. Ensure your server is running as described above.

#### Start Ngrok:
1. Open a terminal and run Ngrok to expose your server port (default is 9999) to the internet:
    ```sh
    ngrok tcp 9999
    ```

#### Configure the Client:
1. Note the forwarding address provided by Ngrok (e.g., `0.tcp.ngrok.io:12345`).
2. Modify the `client.py` script to connect to the provided Ngrok address:
    ```python
    client.connect(("0.tcp.ngrok.io", 12345))
    ```

#### Run the Client:
1. Run your client as usual, and it should now connect to your server via Ngrok.

## Usage

### General Use
1. Start the server.
2. Connect clients using the client script. Enter a unique username for each client. If the username is "admin", you will be prompted for a password.
3. Send messages from one client to see them appear in others.

### Admin Commands
- **Kick a User**: Type `/kick username` to remove a user from the chat.
- **Ban a User**: Type `/ban username` to ban a user permanently.
- **Shutdown Server**: Type `/shutdown` to gracefully stop the server and disconnect all clients.
