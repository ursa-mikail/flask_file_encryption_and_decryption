from flask import Flask, render_template, request, send_file, jsonify
import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import base64
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class FileEncryptor:
    def __init__(self):
        self.backend = default_backend()
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive AES key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(password.encode())
        return key
    
    def encrypt_file(self, input_path: str, output_path: str, password: str) -> dict:
        """Encrypt file using AES-GCM"""
        try:
            # Generate salt and nonce
            salt = secrets.token_bytes(16)
            nonce = secrets.token_bytes(12)
            
            # Derive key
            key = self.derive_key(password, salt)
            
            # Initialize AES-GCM
            aesgcm = AESGCM(key)
            
            # Read file content
            with open(input_path, 'rb') as f:
                plaintext = f.read()
            
            # Encrypt data
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Write encrypted file (salt + nonce + ciphertext)
            with open(output_path, 'wb') as f:
                f.write(salt)
                f.write(nonce)
                f.write(ciphertext)
            
            # Return metadata
            return {
                'input_file': os.path.basename(input_path),
                'output_file': os.path.basename(output_path),
                'salt': base64.b64encode(salt).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'password': password  # Store password in metadata
            }
        except Exception as e:
            print(f"Encryption error: {e}")
            raise e
    
    def decrypt_file(self, input_path: str, output_path: str, password: str, salt_b64: str = None, nonce_b64: str = None) -> bool:
        """Decrypt file using AES-GCM"""
        try:
            # Read encrypted file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            if salt_b64 and nonce_b64:
                # Use provided salt and nonce from metadata
                salt = base64.b64decode(salt_b64)
                nonce = base64.b64decode(nonce_b64)
                # The file still contains salt+nonce+ciphertext, so skip first 28 bytes
                if len(data) < 28:
                    raise ValueError("File too short to contain salt and nonce")
                ciphertext = data[28:]  # Skip salt (16 bytes) + nonce (12 bytes)
                print(f"Metadata method - Salt from metadata: {len(salt)} bytes, Nonce from metadata: {len(nonce)} bytes, Ciphertext: {len(ciphertext)} bytes")
            else:
                # Extract salt and nonce from file (manual method)
                if len(data) < 28:  # 16 bytes salt + 12 bytes nonce
                    raise ValueError("File too short to contain salt and nonce")
                salt = data[:16]
                nonce = data[16:28]
                ciphertext = data[28:]
                print(f"Manual method - Salt from file: {len(salt)} bytes, Nonce from file: {len(nonce)} bytes, Ciphertext: {len(ciphertext)} bytes")
            
            # Derive key
            key = self.derive_key(password, salt)
            
            # Initialize AES-GCM and decrypt
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            return True
        except Exception as e:
            print(f"Decryption error: {e}")
            return False

# Initialize encryptor
encryptor = FileEncryptor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get password
        password = request.form.get('password')
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Get output filename
        output_name = request.form.get('output_name')
        if not output_name:
            output_name = file.filename + '.enc'
        elif not output_name.endswith('.enc'):
            output_name += '.enc'
        
        # Save uploaded file temporarily
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_path)
        
        # Encrypt file
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)
        metadata = encryptor.encrypt_file(input_path, output_path, password)
        
        # Create metadata file
        meta_filename = output_name + '.meta'
        meta_path = os.path.join(app.config['UPLOAD_FOLDER'], meta_filename)
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            'success': True,
            'encrypted_file': output_name,
            'metadata_file': meta_filename,
            'metadata': metadata
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    try:
        # Check if using metadata file or manual input
        use_metadata = request.form.get('use_metadata') == 'true'
        
        if use_metadata:
            # Handle metadata file upload
            if 'meta_file' not in request.files:
                return jsonify({'error': 'No metadata file selected'}), 400
            
            meta_file = request.files['meta_file']
            if meta_file.filename == '':
                return jsonify({'error': 'No metadata file selected'}), 400
            
            # Handle encrypted file upload
            if 'encrypted_file' not in request.files:
                return jsonify({'error': 'No encrypted file selected'}), 400
            
            encrypted_file = request.files['encrypted_file']
            if encrypted_file.filename == '':
                return jsonify({'error': 'No encrypted file selected'}), 400
            
            # Save metadata file
            meta_path = os.path.join(app.config['UPLOAD_FOLDER'], meta_file.filename)
            meta_file.save(meta_path)
            
            # Save encrypted file
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_file.filename)
            encrypted_file.save(input_path)
            
            # Read metadata
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            # Get ALL parameters from metadata
            password = metadata['password']  # Get password from metadata
            salt_b64 = metadata['salt']
            nonce_b64 = metadata['nonce']
            
            # Clean up metadata file
            if os.path.exists(meta_path):
                os.remove(meta_path)
        
        else:
            # Manual input
            if 'encrypted_file' not in request.files:
                return jsonify({'error': 'No encrypted file selected'}), 400
            
            encrypted_file = request.files['encrypted_file']
            if encrypted_file.filename == '':
                return jsonify({'error': 'No encrypted file selected'}), 400
            
            input_filename = encrypted_file.filename
            password = request.form.get('password')  # Get password from form
            salt_b64 = None
            nonce_b64 = None
            
            if not password:
                return jsonify({'error': 'Password is required'}), 400
            
            # Save encrypted file
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            encrypted_file.save(input_path)
        
        # Get output filename
        output_name = request.form.get('output_name')
        if not output_name:
            if use_metadata:
                # Use original filename from metadata
                output_name = metadata.get('input_file', 'decrypted_file')
            else:
                # Remove .enc extension if present
                if 'input_filename' in locals() and input_filename.endswith('.enc'):
                    output_name = input_filename[:-4]
                else:
                    output_name = 'decrypted_file'
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)
        
        # Decrypt file
        success = encryptor.decrypt_file(input_path, output_path, password, salt_b64, nonce_b64)
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        if success:
            return jsonify({
                'success': True,
                'decrypted_file': output_name
            })
        else:
            return jsonify({'error': 'Decryption failed. Please check your files and try again.'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Decryption error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)