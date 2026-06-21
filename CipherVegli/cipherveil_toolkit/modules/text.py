from cipherveil_toolkit.utils import bytes_to_bits, bits_to_bytes
from cipherveil_toolkit.crypto import encrypt, decrypt
import struct
import os

ZERO_WIDTH_0 = '\u200B'
ZERO_WIDTH_1 = '\u200C'
ZERO_WIDTH_SEP = '\u200D'

def encode(input_path: str, payload_str: str, output_path: str, password: str = None) -> bool:
    with open(input_path, 'r', encoding='utf-8') as f:
        cover_text = f.read()
        
    if not cover_text:
        cover_text = " "
        
    payload_bytes = payload_str.encode('utf-8')
    if password:
        payload_bytes = encrypt(payload_bytes, password)
        
    length_header = struct.pack('>I', len(payload_bytes))
    data_to_hide = length_header + payload_bytes
    bits_to_hide = bytes_to_bits(data_to_hide)
    
    hidden_str = ZERO_WIDTH_SEP
    for bit in bits_to_hide:
        if bit == '0':
            hidden_str += ZERO_WIDTH_0
        else:
            hidden_str += ZERO_WIDTH_1
    hidden_str += ZERO_WIDTH_SEP
    
    # Insert after first character
    stego_text = cover_text[:1] + hidden_str + cover_text[1:]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(stego_text)
        
    return True

def decode(input_path: str, password: str = None) -> str:
    with open(input_path, 'r', encoding='utf-8') as f:
        stego_text = f.read()
        
    start_idx = stego_text.find(ZERO_WIDTH_SEP)
    if start_idx == -1:
        raise ValueError("No hidden payload found.")
        
    end_idx = stego_text.find(ZERO_WIDTH_SEP, start_idx + 1)
    if end_idx == -1:
        raise ValueError("Malformed hidden payload (no end separator).")
        
    hidden_str = stego_text[start_idx+1:end_idx]
    
    extracted_bits = ''
    for char in hidden_str:
        if char == ZERO_WIDTH_0:
            extracted_bits += '0'
        elif char == ZERO_WIDTH_1:
            extracted_bits += '1'
            
    if len(extracted_bits) < 32:
        raise ValueError("Hidden payload too short to contain header.")
        
    payload_len = struct.unpack('>I', bits_to_bytes(extracted_bits[:32]))[0]
    total_bits_to_read = 32 + (payload_len * 8)
    
    if len(extracted_bits) < total_bits_to_read:
        raise ValueError("Decoded length exceeds extracted bits. Data corrupted.")
        
    payload_bits = extracted_bits[32:total_bits_to_read]
    payload_bytes = bits_to_bytes(payload_bits)
    
    if password:
        try:
            payload_bytes = decrypt(payload_bytes, password)
        except Exception as e:
            raise ValueError(f"Decryption failed. Incorrect password or corrupted data: {e}")
            
    return payload_bytes.decode('utf-8')
