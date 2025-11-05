#

Encryption:
```
Go to the "Encrypt File" tab
Select a file to encrypt

Enter a strong password

(Optional) Specify output filename

Click "Encrypt File"

Download both the encrypted file and metadata file
```

Decryption:
```
Method 1 - Using Metadata:
Go to "Decrypt File" tab
Select "Use Metadata File"
Upload your .meta file
Click "Decrypt File with Metadata"

Method 2 - Manual Input:
Go to "Decrypt File" tab
Select "Manual Input"
Upload the encrypted file
Enter the password

(Optional) Provide the salt from metadata
Click "Decrypt File"
```

Features Included:
```
✅ File encryption with AES-GCM
✅ Password-based key derivation (PBKDF2)
✅ Automatic metadata generation
✅ Flexible decryption options
✅ Web-based interface
✅ File download functionality
✅ Error handling
✅ Secure random salt/nonce generation
```

Security Notes:
```
Uses PBKDF2 with 100,000 iterations for key derivation

AES-GCM provides both confidentiality and authentication

Random salts and nonces are generated for each operation

Files are temporarily stored and automatically cleaned up

No passwords are stored on the server

The application provides a complete, secure file encryption/decryption solution with a user-friendly web interface!
```

```
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install flask cryptography # pip install -r requirements.txt


http://localhost:5000
```

```
make run
make clean
```


