import PyPDF2
from cipherveil_toolkit.crypto import encrypt, decrypt
import base64

def encode(input_path: str, payload_str: str, output_path: str, password: str = None, method: str = 'metadata') -> bool:
    if method != 'metadata':
        raise NotImplementedError("Only 'metadata' method is currently implemented.")
        
    payload_bytes = payload_str.encode('utf-8')
    if password:
        payload_bytes = encrypt(payload_bytes, password)
        
    payload_b64 = base64.b64encode(payload_bytes).decode('utf-8')
    
    reader = PyPDF2.PdfReader(input_path)
    writer = PyPDF2.PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    metadata = reader.metadata
    new_metadata = {}
    if metadata:
        new_metadata.update(metadata)
        
    new_metadata['/Keywords'] = payload_b64
    
    writer.add_metadata(new_metadata)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
        
    return True

def decode(input_path: str, password: str = None, method: str = 'metadata') -> str:
    if method != 'metadata':
        raise NotImplementedError("Only 'metadata' method is currently implemented.")
        
    reader = PyPDF2.PdfReader(input_path)
    metadata = reader.metadata
    
    if not metadata or '/Keywords' not in metadata:
        raise ValueError("No hidden payload found in metadata.")
        
    payload_b64 = metadata['/Keywords']
    
    try:
        payload_bytes = base64.b64decode(payload_b64)
    except Exception:
        raise ValueError("Malformed payload.")
        
    if password:
        try:
            payload_bytes = decrypt(payload_bytes, password)
        except Exception as e:
            raise ValueError(f"Decryption failed. Incorrect password or corrupted data: {e}")
            
    return payload_bytes.decode('utf-8')
