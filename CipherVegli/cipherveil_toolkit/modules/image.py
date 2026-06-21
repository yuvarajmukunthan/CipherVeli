from PIL import Image
from cipherveil_toolkit.utils import bytes_to_bits, bits_to_bytes
from cipherveil_toolkit.crypto import encrypt, decrypt
import os
import struct

def calculate_capacity(img: Image.Image) -> int:
    """Calculate the maximum capacity in bytes for a given image."""
    pixels = img.size[0] * img.size[1]
    channels = len(img.getbands())
    total_bits = pixels * channels
    max_payload_bits = total_bits - 32
    return max_payload_bits // 8

def encode(input_path: str, payload_str: str, output_path: str, password: str = None) -> bool:
    """Encode a payload string into an image."""
    img = Image.open(input_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')

    payload_bytes = payload_str.encode('utf-8')
    if password:
        payload_bytes = encrypt(payload_bytes, password)

    capacity = calculate_capacity(img)
    if len(payload_bytes) > capacity:
        raise ValueError(f"Payload too large. Max capacity is {capacity} bytes, but payload is {len(payload_bytes)} bytes.")

    length_header = struct.pack('>I', len(payload_bytes))
    data_to_hide = length_header + payload_bytes
    bits_to_hide = bytes_to_bits(data_to_hide)
    bits_len = len(bits_to_hide)

    encoded_img = img.copy()
    pixels = encoded_img.load()
    width, height = img.size
    channels = len(img.getbands())
    
    bit_idx = 0
    
    for y in range(height):
        for x in range(width):
            if bit_idx >= bits_len:
                break
            
            pixel = list(pixels[x, y])
            for i in range(channels):
                if bit_idx < bits_len:
                    pixel[i] = (pixel[i] & ~1) | int(bits_to_hide[bit_idx])
                    bit_idx += 1
            pixels[x, y] = tuple(pixel)
        if bit_idx >= bits_len:
            break

    ext = os.path.splitext(output_path)[1].lower()
    fmt = 'PNG' if ext == '.png' else 'BMP'
    encoded_img.save(output_path, format=fmt)
    return True

def decode(input_path: str, password: str = None) -> str:
    """Decode a payload string from an image."""
    img = Image.open(input_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')
        
    pixels = img.load()
    width, height = img.size
    channels = len(img.getbands())
    
    extracted_bits = ''
    
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for i in range(channels):
                extracted_bits += str(pixel[i] & 1)
                if len(extracted_bits) == 32:
                    break
            if len(extracted_bits) == 32:
                break
        if len(extracted_bits) == 32:
            break
            
    if len(extracted_bits) < 32:
        raise ValueError("Could not extract length header.")
        
    payload_len = struct.unpack('>I', bits_to_bytes(extracted_bits))[0]
    total_bits_to_read = 32 + (payload_len * 8)
    
    max_bits = width * height * channels
    if total_bits_to_read > max_bits:
        raise ValueError("Decoded length exceeds image capacity. Data might be corrupted or no payload exists.")
        
    extracted_bits = ''
    bits_read = 0
    
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for i in range(channels):
                if bits_read < total_bits_to_read:
                    extracted_bits += str(pixel[i] & 1)
                    bits_read += 1
                else:
                    break
            if bits_read >= total_bits_to_read:
                break
        if bits_read >= total_bits_to_read:
            break

    payload_bits = extracted_bits[32:]
    payload_bytes = bits_to_bytes(payload_bits)

    if password:
        try:
            payload_bytes = decrypt(payload_bytes, password)
        except Exception as e:
            raise ValueError(f"Decryption failed. Incorrect password or corrupted data: {e}")

    return payload_bytes.decode('utf-8')
