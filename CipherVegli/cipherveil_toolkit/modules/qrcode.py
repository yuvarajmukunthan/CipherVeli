import qrcode
from cipherveil_toolkit.modules import image
import os

def encode(data: str, payload_str: str, output_path: str, password: str = None) -> bool:
    """Generate a QR code and embed the payload."""
    qr = qrcode.QRCode(
        version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=10, 
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    temp_path = output_path + ".temp.png"
    img.save(temp_path)
    
    try:
        image.encode(temp_path, payload_str, output_path, password)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return True

def decode(input_path: str, password: str = None) -> str:
    """Decode a payload from a QR code image."""
    return image.decode(input_path, password)
