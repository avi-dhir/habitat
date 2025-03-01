import os
import base64
from cryptography.fernet import Fernet

def generate_key():
    """Generates a new encryption key."""
    return Fernet.generate_key()

def encrypt_text(input_text, filename="output.kne"):
    """Encrypts text using a format that includes invalid Unicode sequences, making it unreadable in standard text editors."""
    key = generate_key()
    cipher = Fernet(key)
    
    encrypted_text = cipher.encrypt(input_text.encode())
    scrambled_binary = key + b"\n" + encrypted_text
    
    scrambled_binary = bytes([b ^ 0xFF for b in scrambled_binary])
    
    with open(filename, "wb") as file:
        file.write(scrambled_binary) 
    
    print(f"Encrypted text saved to {filename}")

def decrypt_text(filename="output.kne"):
    """Decrypts a file that contains both the key and encrypted text with invalid Unicode bytes."""
    with open(filename, "rb") as file:
        scrambled_binary = file.read()
    
    scrambled_binary = bytes([b ^ 0xFF for b in scrambled_binary])
    
    file_content = scrambled_binary.split(b"\n", 1) 
    
    if len(file_content) < 2:
        raise ValueError("Invalid encrypted file format.")
    
    key, encrypted_text = file_content
    cipher = Fernet(key)
    
    decrypted_text = cipher.decrypt(encrypted_text).decode()
    return decrypted_text

# Example Usage
if __name__ == "__main__":
    text = "This is a test string for encryption."
    encrypt_text(text, "filename.hbt")
    
    decrypted = decrypt_text("filename.hbt")
    print("Decrypted Text:", decrypted)
