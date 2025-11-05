from flask import Flask, render_template, request, send_file, jsonify
import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class FileEncryptor:
    def __init__(self):
        pass
    
    def generate_key(self) -> tuple:
        """Generate a random 256-bit AES key"""
        key = secrets.token_bytes(32)  # 256 bits
        key_hex = key.hex()
        key_b64 = base64.b64encode(key).decode('utf-8')
        return key, key_hex, key_b64
    
    def parse_key(self, key_input: str) -> bytes:
        """Parse key from hex or base64 format"""
        try:
            # Try hex first
            if len(key_input) == 64 and all(c in '0123456789abcdefABCDEF' for c in key_input):
                key = bytes.fromhex(key_input)
            else:
                # Try base64
                key = base64.b64decode(key_input)
        except Exception as e:
            raise ValueError(f"Invalid key format. Please provide a valid hex or base64 key: {str(e)}")
        
        if len(key) != 32:
            raise ValueError("Key must be 256 bits (32 bytes)")
        
        return key
    
    def encrypt_file(self, input_path: str, output_path: str, key_input: str = None) -> dict:
        """Encrypt file using AES-GCM with provided or randomly generated key"""
        try:
            # Use provided key or generate new one
            if key_input:
                key = self.parse_key(key_input)
                key_hex = key.hex()
                key_b64 = base64.b64encode(key).decode('utf-8')
            else:
                key, key_hex, key_b64 = self.generate_key()
            
            # Generate random nonce
            nonce = secrets.token_bytes(12)
            
            # Initialize AES-GCM
            aesgcm = AESGCM(key)
            
            # Read file content
            with open(input_path, 'rb') as f:
                plaintext = f.read()
            
            # Encrypt data
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Write encrypted file (nonce + ciphertext)
            with open(output_path, 'wb') as f:
                f.write(nonce)
                f.write(ciphertext)
            
            # Return metadata
            return {
                'input_file': os.path.basename(input_path),
                'output_file': os.path.basename(output_path),
                'key_hex': key_hex,
                'key_base64': key_b64,
                'nonce': base64.b64encode(nonce).decode('utf-8')
            }
        except Exception as e:
            print(f"Encryption error: {e}")
            raise e
    
    def decrypt_file(self, input_path: str, output_path: str, key_input: str, nonce_b64: str = None) -> bool:
        """Decrypt file using AES-GCM"""
        try:
            # Read encrypted file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Parse key
            key = self.parse_key(key_input)
            
            if nonce_b64:
                # Use provided nonce from metadata
                nonce = base64.b64decode(nonce_b64)
                # The file still contains nonce+ciphertext, so skip first 12 bytes
                if len(data) < 12:
                    raise ValueError("File too short to contain nonce")
                ciphertext = data[12:]  # Skip nonce (12 bytes)
                print(f"Metadata method - Nonce from metadata: {len(nonce)} bytes, Ciphertext: {len(ciphertext)} bytes")
            else:
                # Extract nonce from file (manual method)
                if len(data) < 12:
                    raise ValueError("File too short to contain nonce")
                nonce = data[:12]
                ciphertext = data[12:]
                print(f"Manual method - Nonce from file: {len(nonce)} bytes, Ciphertext: {len(ciphertext)} bytes")
            
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

@app.route('/generate_key', methods=['GET'])
def generate_key():
    """Generate a random key and return it"""
    try:
        key, key_hex, key_b64 = encryptor.generate_key()
        return jsonify({
            'success': True,
            'key_hex': key_hex,
            'key_base64': key_b64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get key (optional - will generate if not provided)
        key_input = request.form.get('key')
        if key_input and key_input.strip():
            key_input = key_input.strip()
        else:
            key_input = None
        
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
        metadata = encryptor.encrypt_file(input_path, output_path, key_input)
        
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
            
            # Get key and nonce from metadata
            key_input = metadata.get('key_base64') or metadata.get('key_hex')
            nonce_b64 = metadata.get('nonce')
            
            if not key_input:
                return jsonify({'error': 'Metadata file does not contain encryption key'}), 400
            
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
            key_input = request.form.get('key')
            nonce_b64 = None
            
            if not key_input:
                return jsonify({'error': 'Encryption key is required'}), 400
            
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
                if input_filename.endswith('.enc'):
                    output_name = input_filename[:-4]
                else:
                    output_name = 'decrypted_file'
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)
        
        # Decrypt file
        success = encryptor.decrypt_file(input_path, output_path, key_input, nonce_b64)
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        if success:
            return jsonify({
                'success': True,
                'decrypted_file': output_name
            })
        else:
            return jsonify({'error': 'Decryption failed. Please check your key and try again.'}), 400
    
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