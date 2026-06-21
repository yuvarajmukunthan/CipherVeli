import subprocess
import os
import struct
from cipherveil_toolkit.utils import bytes_to_bits, bits_to_bytes
from cipherveil_toolkit.crypto import encrypt, decrypt

def encode(repo_path: str, payload_str: str, password: str = None) -> bool:
    payload_bytes = payload_str.encode('utf-8')
    if password:
        payload_bytes = encrypt(payload_bytes, password)
        
    length_header = struct.pack('>I', len(payload_bytes))
    data_to_hide = length_header + payload_bytes
    bits_to_hide = bytes_to_bits(data_to_hide)
    
    whitespace_payload = ''
    for bit in bits_to_hide:
        if bit == '0':
            whitespace_payload += ' '
        else:
            whitespace_payload += '\t'
            
    cover_message = "Update project configuration"
    full_message = cover_message + '\n\n' + whitespace_payload
    
    env = os.environ.copy()
    try:
        subprocess.run(['git', 'commit', '--allow-empty', '--cleanup=verbatim', '-m', full_message], cwd=repo_path, env=env, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Git commit failed: {e.stderr.decode('utf-8')}")
        
    return True

def decode(repo_path: str, password: str = None) -> str:
    try:
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], cwd=repo_path, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Git log failed: {e.stderr.decode('utf-8')}")
        
    commit_msg = result.stdout.decode('utf-8').rstrip('\r\n')
    
    lines = commit_msg.split('\n')
    if not lines or not lines[-1]:
        raise ValueError("No hidden payload found in commit message.")
        
    whitespace_payload = lines[-1]
        
    extracted_bits = ''
    for char in whitespace_payload:
        if char == ' ':
            extracted_bits += '0'
        elif char == '\t':
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
