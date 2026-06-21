import os

def bits_to_bytes(bits: str) -> bytes:
    """Convert a string of bits to bytes."""
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte_str = bits[i:i+8]
        if len(byte_str) < 8:
            byte_str = byte_str.ljust(8, '0')
        b.append(int(byte_str, 2))
    return bytes(b)

def bytes_to_bits(data: bytes) -> str:
    """Convert bytes to a string of bits."""
    return ''.join(f'{byte:08b}' for byte in data)

def detect_format(file_path: str) -> str:
    """Detect the format of a file to determine the steganography module."""
    if os.path.isdir(file_path) and os.path.exists(os.path.join(file_path, '.git')):
        return 'git'
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.png', '.bmp']:
        return 'image'
    elif ext in ['.wav', '.flac']:
        return 'audio'
    elif ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.txt', '.md']:
        return 'text'
    return 'unknown'
