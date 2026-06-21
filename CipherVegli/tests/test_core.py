import unittest
import os
import sys
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PIL import Image
from cipherveil_toolkit import crypto
from cipherveil_toolkit import utils
from cipherveil_toolkit.modules import text, image, git

class TestCipherVeil(unittest.TestCase):
    
    def test_crypto(self):
        payload = b"Secret payload 123"
        password = "strongpassword"
        
        encrypted = crypto.encrypt(payload, password)
        self.assertNotEqual(payload, encrypted)
        
        decrypted = crypto.decrypt(encrypted, password)
        self.assertEqual(payload, decrypted)
        
        with self.assertRaises(Exception):
            crypto.decrypt(encrypted, "wrongpassword")
            
    def test_utils(self):
        data = b"Hello"
        bits = utils.bytes_to_bits(data)
        self.assertEqual(len(bits), len(data) * 8)
        
        decoded = utils.bits_to_bytes(bits)
        self.assertEqual(data, decoded)
        
    def test_text_module(self):
        payload = "Confidential data"
        password = "testpass"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Normal looking cover text.")
            input_path = f.name
            
        output_path = input_path + ".stego"
        
        try:
            text.encode(input_path, payload, output_path, password)
            self.assertTrue(os.path.exists(output_path))
            
            decoded_payload = text.decode(output_path, password)
            self.assertEqual(payload, decoded_payload)
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
                
    def test_image_module(self):
        payload = "Image secret"
        password = "imgpass"
        
        img = Image.new('RGB', (100, 100), color='white')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            input_path = f.name
        img.save(input_path)
        
        output_path = input_path + ".stego.png"
        
        try:
            image.encode(input_path, payload, output_path, password)
            self.assertTrue(os.path.exists(output_path))
            
            decoded_payload = image.decode(output_path, password)
            self.assertEqual(payload, decoded_payload)
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_git_module(self):
        import subprocess
        import shutil
        
        payload = "Git commit payload"
        password = "gitpassword"
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True, check=True)
            
            # Configure git for test environment
            subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True, check=True)
            
            # Commit payload
            git.encode(temp_dir, payload, password)
            
            # Decode payload
            decoded = git.decode(temp_dir, password)
            self.assertEqual(payload, decoded)
            
            # Decode using detect_format & CLI decode helper path
            fmt = utils.detect_format(temp_dir)
            self.assertEqual(fmt, 'git')
        finally:
            # Clean up directory (using onerror to handle git read-only files on Windows)
            def on_error(func, path, exc_info):
                import stat
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception:
                    pass
            shutil.rmtree(temp_dir, onerror=on_error)

if __name__ == '__main__':
    unittest.main()
