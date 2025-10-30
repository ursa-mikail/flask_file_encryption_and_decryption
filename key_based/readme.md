# File Encryption Tool

A secure web-based file encryption/decryption tool using AES-GCM with randomly generated 256-bit keys.

```
http://localhost:5000/generate_key


{
  "key_base64": "i/AlIkBtP5JgpiV9fOTlvTL73Ww4hSGSrfz0Qr2siKY=",
  "key_hex": "8bf02522406d3f9260a6257d7ce4e5bd32fbdd6c38852192adfcf442bdac88a6",
  "success": true
}
```

## Features

✅ **Strong Encryption**: AES-GCM (256-bit keys)  
✅ **Random Key Generation**: Cryptographically secure random keys  
✅ **Dual Key Format**: Keys provided in both Hex and Base64  
✅ **Automatic Metadata**: Saves encryption parameters for easy decryption  
✅ **Flexible Decryption**: Use metadata file or manual key input  
✅ **Web Interface**: User-friendly Flask-based UI  
✅ **Secure**: No keys stored on server, automatic cleanup  

## Quick Start

### Installation

```bash
# Clone the repository
cd your-encryption-tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install flask cryptography
# OR
pip install -r requirements.txt
```

### Run the Application

```bash
# Using Python directly
python app.py

# OR using Makefile
make run

# OR open in Chrome automatically
make run-chrome
```

Then navigate to `http://localhost:5000`

## Usage

### Encrypting a File

1. Go to the **"Encrypt File"** tab
2. Select a file to encrypt
3. (Optional) Specify output filename
4. Click **"Encrypt File"**
5. **Save the encryption key** (displayed in both Hex and Base64 format)
6. Download both the encrypted file and metadata file

**⚠️ CRITICAL:** Save your encryption key securely! Without it, you cannot decrypt your file.

### Decrypting a File

#### Method 1: Using Metadata File (Easiest)

1. Go to **"Decrypt File"** tab
2. Select **"Use Metadata File"**
3. Upload the encrypted file (.enc)
4. Upload the metadata file (.meta)
5. Click **"Decrypt File with Metadata"**
6. Download your decrypted file

#### Method 2: Manual Key Input

1. Go to **"Decrypt File"** tab
2. Select **"Manual Key Input"**
3. Upload the encrypted file
4. Enter the encryption key (Hex or Base64 format)
5. Click **"Decrypt File"**
6. Download your decrypted file

## Technical Details

### Encryption Process

1. **Key Generation**: Random 256-bit (32-byte) AES key using `secrets.token_bytes()`
2. **Nonce Generation**: Random 12-byte nonce for AES-GCM
3. **Encryption**: AES-GCM mode (provides authentication + confidentiality)
4. **File Structure**: `[12-byte nonce][ciphertext]`
5. **Metadata**: JSON file containing:
   - Original filename
   - Output filename
   - Encryption key (Hex format)
   - Encryption key (Base64 format)
   - Nonce (Base64)

### Key Formats

- **Hex Format**: 64 hexadecimal characters (e.g., `a1b2c3d4...`)
- **Base64 Format**: 44 base64 characters (e.g., `obPD1O...==`)

Both formats represent the same 256-bit key and are interchangeable.

### Security Features

- **Cryptographically Secure RNG**: Uses `secrets` module for key/nonce generation
- **AES-GCM**: Provides both encryption and authentication
- **No Password Derivation**: Direct use of random keys (stronger than password-based)
- **Temporary Storage**: Files cleaned up after processing
- **No Server-Side Storage**: Keys never stored on server

## File Structure

```
.
├── app.py                  # Flask application
├── Makefile               # Build automation
├── readme.md              # This file
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/
│   └── index.html        # Main HTML template
└── uploads/              # Temporary file storage (auto-created)
```

## Makefile Commands

```bash
make setup      # First-time setup (create venv + install deps)
make install    # Install dependencies
make run        # Run the application
make run-chrome # Run and open in Chrome
make clean      # Clean temporary files
make venv       # Create virtual environment only
make info       # Show project information
```

## Security Considerations

### ✅ Do's

- Save your encryption keys in a secure password manager
- Keep metadata files safe (they contain the encryption key)
- Use strong physical security for stored keys
- Back up your keys separately from encrypted files

### ❌ Don'ts

- Don't share your encryption keys via insecure channels
- Don't lose your keys (data will be irrecoverable)
- Don't use this for extremely sensitive data without additional security measures
- Don't trust the server in a multi-user environment (deploy privately)

## API Endpoints

### `POST /encrypt`
- **Input**: File upload (multipart/form-data)
- **Output**: Encrypted file + metadata file
- **Returns**: JSON with download links and encryption key

### `POST /decrypt`
- **Input**: Encrypted file + (metadata file OR manual key)
- **Output**: Decrypted file
- **Returns**: JSON with download link

### `GET /download/<filename>`
- **Input**: Filename
- **Output**: File download

## Dependencies

- **Flask 2.3.3**: Web framework
- **cryptography 41.0.3**: Encryption library
- **Werkzeug 2.3.7**: WSGI utilities

## Example Metadata File

```json
{
  "input_file": "document.pdf",
  "output_file": "document.pdf.enc",
  "key_hex": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "key_base64": "obPD1OX29ofYie+qr7sufXy9zv+Dg4ODg4ODg4ODg4M=",
  "nonce": "YWJjZGVmZ2hpams="
}
```

## Troubleshooting

### "Invalid key format" error
- Ensure key is exactly 64 hex characters OR valid base64
- Check for extra spaces or line breaks

### "Decryption failed" error
- Verify you're using the correct key for the file
- Ensure the encrypted file hasn't been corrupted
- Check that metadata matches the encrypted file

### Port already in use
- Change port: `PORT=5001 python app.py`
- Or kill process using port 5000

## License

This tool is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues and pull requests.

## Disclaimer

This tool is intended for personal use and learning purposes. For production use with sensitive data, conduct a thorough security audit and consider additional security measures such as:
- HTTPS/TLS for web traffic
- Authentication and authorization
- Secure key management systems
- Regular security updates
