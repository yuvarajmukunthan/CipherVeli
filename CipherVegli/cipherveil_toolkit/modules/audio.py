import soundfile as sf
import numpy as np
from cipherveil_toolkit.utils import bytes_to_bits, bits_to_bytes
from cipherveil_toolkit.crypto import encrypt, decrypt
import os
import struct

def calculate_capacity(data: np.ndarray) -> int:
    """Calculate the maximum capacity in bytes for a given audio array."""
    total_samples = data.size
    max_payload_bits = total_samples - 32
    return max_payload_bits // 8

def encode(input_path: str, payload_str: str, output_path: str, password: str = None) -> bool:
    data, samplerate = sf.read(input_path, dtype='int16')
    
    payload_bytes = payload_str.encode('utf-8')
    if password:
        payload_bytes = encrypt(payload_bytes, password)

    capacity = calculate_capacity(data)
    if len(payload_bytes) > capacity:
        raise ValueError(f"Payload too large. Max capacity is {capacity} bytes.")

    length_header = struct.pack('>I', len(payload_bytes))
    data_to_hide = length_header + payload_bytes
    bits_to_hide = bytes_to_bits(data_to_hide)
    bits_len = len(bits_to_hide)

    data_flat = data.flatten()
    
    for i in range(bits_len):
        sample = int(data_flat[i])
        sample = (sample & ~1) | int(bits_to_hide[i])
        data_flat[i] = sample

    if len(data.shape) > 1:
        data_flat = data_flat.reshape(data.shape)
        
    ext = os.path.splitext(output_path)[1].lower()
    fmt = 'FLAC' if ext == '.flac' else 'WAV'
    sf.write(output_path, data_flat, samplerate, format=fmt, subtype='PCM_16')
    return True

def decode(input_path: str, password: str = None) -> str:
    data, _ = sf.read(input_path, dtype='int16')
    data_flat = data.flatten()
    
    if data_flat.size < 32:
        raise ValueError("Audio file too small to contain a payload.")
        
    extracted_bits = ''
    for i in range(32):
        extracted_bits += str(data_flat[i] & 1)
        
    payload_len = struct.unpack('>I', bits_to_bytes(extracted_bits))[0]
    total_bits_to_read = 32 + (payload_len * 8)
    
    if total_bits_to_read > data_flat.size:
        raise ValueError("Decoded length exceeds audio capacity. Data might be corrupted or no payload exists.")
        
    extracted_bits = ''
    for i in range(total_bits_to_read):
        extracted_bits += str(data_flat[i] & 1)

    payload_bits = extracted_bits[32:]
    payload_bytes = bits_to_bytes(payload_bits)

    if password:
        try:
            payload_bytes = decrypt(payload_bytes, password)
        except Exception as e:
            raise ValueError(f"Decryption failed. Incorrect password or corrupted data: {e}")

    return payload_bytes.decode('utf-8')
