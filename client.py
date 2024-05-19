import re
import sys
import socket
import threading
import subprocess

from googletrans import Translator
from cryptography.fernet import Fernet

import base64
import binascii
from typing import Optional, Dict


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
        'socket': 'socket',
        'threading': 'threading',
        'googletrans': 'googletrans==4.0.0-rc1',
        'cryptography': 'cryptography'
    }

    for module_name, package_name in packages.items():
        install_and_import(package_name, module_name)


check_and_install_packages()

translator = Translator()


def receive_messages(client_socket: socket.socket, cipher: Fernet, language: str) -> None:
    """
    Receives and decrypts messages from the server, translating them to the specified language.

    Args:
    client_socket: The client socket connected to the server.
    cipher: The Fernet cipher used for decrypting messages.
    language: The target language code for translation.
    """
    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if encrypted_message:
                message = cipher.decrypt(encrypted_message).decode('utf-8')
                translated_message = translator.translate(message, dest=language).text
                print(f"\n{translated_message}")
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def display_languages(languages: Dict[str, str]) -> None:
    """
    Displays the available languages.

    Args:
    languages: A dictionary of language codes and their corresponding names.
    """
    sorted_languages = sorted(languages.items(), key=lambda x: x[1])
    print("\nAvailable languages:")
    for i, (code, language) in enumerate(sorted_languages, 1):
        if len(language) == 17:
            print(f"{code}: {language}", end="\t\t")
        elif len(language) > 16:
            print(f"{code}: {language}", end="\t\t")
        elif len(language) > 11:
            print(f"{code}: {language}", end="\t\t\t")
        elif len(language) <= 3:
            print(f"{code}: {language}", end="\t\t\t\t\t")
        else:
            print(f"{code}: {language}", end="\t\t\t\t")
        if i % 4 == 0:
            print()
    print()


def is_valid_ip(address: str) -> bool:
    """
    Validates if the given address is a valid IP address or an ngrok address.

    Args:
    address: The address to validate.

    Returns:
    True if the address is valid, False otherwise.
    """
    ip_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    ngrok_pattern = re.compile(r'^[0-9]+\.tcp\.ngrok\.io$')
    return bool(ip_pattern.match(address) or ngrok_pattern.match(address))


# ASCII Art Welcome Message
welcome_message = """
    ____    _____      ____ _           _   
   |_  _|  /  _  \    / ___| |__   __ _| |_ 
    |  |  |  | |  |  | |   | '_ \ / _` | __|
    |  |  |  |_|  |  | |___| | | | (_| | |_ 
   |____|  \_____/    \____|_| |_|\__,_|\__|
"""

print(welcome_message)
print("Welcome to an encrypted, auto-translation chatroom\nthat filters negative messages")

# Ask for the server address, port number, name, and language
while True:
    server_address = input("\nEnter server address (IP or ngrok address): ")
    if server_address.strip() and is_valid_ip(server_address):
        break
    print("Invalid address. Please enter a valid server address.")

while True:
    port = input("Enter port number: ")
    if port.strip() and port.isdigit():
        break
    print("Please enter a valid port number.")

while True:
    name = input("\nEnter your name: ")
    if name.strip():
        break
    print("Please enter a valid name.")

# Available languages dictionary
languages = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani',
    'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian',
    'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
    'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian',
    'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
    'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi', 'mn': 'Mongolian', 'ne': 'Nepali', 'no': 'Norwegian',
    'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian',
    'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
    'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish',
    'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu',
    'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese',
    'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

display_languages(languages)

language = input("\nEnter your preferred language code (e.g., 'en' for English - default language if none chosen): ")

# Set default language to English if no language is chosen
if not language:
    language = 'en'

max_attempts = 5
attempts = 0

while attempts < max_attempts:
    key = input("\nEnter the encryption key provided by the server: ")
    if key.strip():
        try:
            missing_padding = len(key) % 4
            if missing_padding:
                key += '=' * (4 - missing_padding)
                key = base64.urlsafe_b64decode(key.encode())
                cipher = Fernet(key)
                break
        except (binascii.Error, ValueError) as e:
            attempts += 1
            print(f"Invalid encryption key ({attempts}/{max_attempts} attempts): {e}")
            if attempts == max_attempts:
                print("Max attempts reached. Please check the encryption key provided by the server.")
                sys.exit(1)
        else:
            print("Please enter a valid encryption key.")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_address, int(port)))

client.send(name.encode('utf-8'))

receive_thread = threading.Thread(target=receive_messages, args=(client, cipher, language))
receive_thread.start()

print("\nYou can type a message at any time. Hit enter to send.")

while True:
    try:
        message = input()
        if message.strip():
            encrypted_message = cipher.encrypt(message.encode('utf-8'))
            client.send(encrypted_message)
    except BrokenPipeError:
        print("Connection to server lost. Exiting program.")
        break
    except Exception as e:
        print(f"Error sending message: {e}")