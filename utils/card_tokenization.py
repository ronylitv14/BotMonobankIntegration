import os

from binascii import unhexlify
from dotenv import load_dotenv

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

load_dotenv()

encoded_key = os.getenv('ENCRYPTION_KEY')
encoded_iv = os.getenv('IV')

KEY = unhexlify(encoded_key)
IV = unhexlify(encoded_iv)


def encrypt_card_number(card_number, key=KEY, iv=IV):
    data = card_number.encode()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data


def decrypt_card_number(encrypted_data, key=KEY, iv=IV):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data.decode()
