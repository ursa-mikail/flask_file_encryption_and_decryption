// Tab management
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Toggle custom key input
function toggleCustomKey() {
    const customKeyInput = document.getElementById('customKeyInput');
    const keyDisplay = document.getElementById('keyDisplay');
    const useCustom = document.getElementById('useCustomKey').checked;
    
    customKeyInput.style.display = useCustom ? 'block' : 'none';
    if (useCustom) {
        keyDisplay.style.display = 'none';
    }
}

// Toggle between manual and metadata decryption methods
function toggleDecryptMethod() {
    const manualMethod = document.getElementById('manual').checked;
    document.getElementById('decryptManualForm').style.display = manualMethod ? 'block' : 'none';
    document.getElementById('decryptMetaForm').style.display = manualMethod ? 'none' : 'block';
}

// Show loading state on buttons
function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.setAttribute('data-original-text', button.textContent);
        button.textContent = 'Processing...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text') || button.textContent;
    }
}

// Copy key to clipboard
function copyKey(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    
    // Visual feedback
    const originalBg = element.style.backgroundColor;
    element.style.backgroundColor = '#d4edda';
    setTimeout(() => {
        element.style.backgroundColor = originalBg;
    }, 300);
}

// Generate random key
document.getElementById('generateKeyBtn').addEventListener('click', async function() {
    const button = this;
    console.log('=== Generate Key Button Clicked ===');
    setLoading(button, true);
    
    try {
        console.log('Fetching /generate_key...');
        const response = await fetch('/generate_key');
        console.log('Response received:', response.status);
        
        const data = await response.json();
        console.log('Data received:', data);
        
        if (data.success) {
            console.log('✓ Key generated successfully');
            console.log('Hex:', data.key_hex);
            console.log('Base64:', data.key_base64);
            
            // Get elements
            const hexField = document.getElementById('keyHexDisplay');
            const base64Field = document.getElementById('keyBase64Display');
            const keyDisplay = document.getElementById('keyDisplay');
            
            console.log('Elements found:', {
                hexField: !!hexField,
                base64Field: !!base64Field,
                keyDisplay: !!keyDisplay
            });
            
            if (!hexField || !base64Field || !keyDisplay) {
                alert('ERROR: Could not find display elements! Check HTML.');
                console.error('Missing elements:', {hexField, base64Field, keyDisplay});
                return;
            }
            
            // Set values - using both .value and .textContent to be sure
            hexField.value = data.key_hex;
            hexField.textContent = data.key_hex;
            base64Field.value = data.key_base64;
            base64Field.textContent = data.key_base64;
            
            console.log('Values set:', {
                hexValue: hexField.value,
                hexText: hexField.textContent,
                base64Value: base64Field.value,
                base64Text: base64Field.textContent
            });
            
            // Force display to show with inline style and multiple methods
            keyDisplay.style.display = 'block';
            keyDisplay.style.visibility = 'visible';
            keyDisplay.style.opacity = '1';
            keyDisplay.style.height = 'auto';
            keyDisplay.removeAttribute('hidden');
            
            console.log('Display shown. Computed style:', window.getComputedStyle(keyDisplay).display);
            
            // Store in custom key field
            const customKeyField = document.getElementById('customKey');
            if (customKeyField) {
                customKeyField.value = data.key_hex;
                console.log('Custom key field set');
            }
            
            // Uncheck and hide custom key option
            const useCustomCheckbox = document.getElementById('useCustomKey');
            const customKeyInput = document.getElementById('customKeyInput');
            if (useCustomCheckbox) useCustomCheckbox.checked = false;
            if (customKeyInput) customKeyInput.style.display = 'none';
            
            // Visual feedback
            const keyDisplayBox = document.querySelector('.key-display-box');
            if (keyDisplayBox) {
                keyDisplayBox.style.animation = 'slideIn 0.3s ease-out';
                keyDisplayBox.style.backgroundColor = '#e3f2fd';
                console.log('Animation and background applied');
            }
            
            // Show a temporary success message
            const successMsg = document.createElement('div');
            successMsg.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 15px 25px; border-radius: 5px; z-index: 9999; font-weight: bold;';
            successMsg.textContent = '✓ Key Generated Successfully!';
            document.body.appendChild(successMsg);
            setTimeout(() => successMsg.remove(), 3000);
            
            console.log('✓✓✓ KEY DISPLAY SHOULD BE VISIBLE NOW ✓✓✓');
        } else {
            console.error('Key generation failed:', data.error);
            alert('Error generating key: ' + data.error);
        }
    } catch (error) {
        console.error('EXCEPTION:', error);
        alert('Network error: ' + error.message);
    } finally {
        setLoading(button, false);
        console.log('=== Generate Key Complete ===');
    }
});

// Encryption form handler
document.getElementById('encryptForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const resultDiv = document.getElementById('encryptResult');
    const submitButton = this.querySelector('button[type="submit"]');
    
    // Get key value (either from custom input or generated key)
    const useCustom = document.getElementById('useCustomKey').checked;
    const keyValue = useCustom ? 
        document.getElementById('customKey').value.trim() : 
        document.getElementById('keyHexDisplay').value;
    
    // Add key to form data if provided
    if (keyValue) {
        formData.set('key', keyValue);
    } else {
        formData.delete('key');
    }
    
    setLoading(submitButton, true);
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch('/encrypt', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <h3>✅ Encryption Successful!</h3>
                <p><strong>Encrypted file:</strong> ${data.encrypted_file}</p>
                <p><strong>Metadata file:</strong> ${data.metadata_file}</p>
                
                <div class="key-display-result">
                    <p><strong>🔑 Your Encryption Key:</strong></p>
                    <div class="key-format">
                        <label>Hex:</label>
                        <div class="key-value-row">
                            <code>${data.metadata.key_hex}</code>
                            <button class="copy-btn-inline" onclick="copyToClipboard('${data.metadata.key_hex}', this)">📋 Copy</button>
                        </div>
                    </div>
                    <div class="key-format">
                        <label>Base64:</label>
                        <div class="key-value-row">
                            <code>${data.metadata.key_base64}</code>
                            <button class="copy-btn-inline" onclick="copyToClipboard('${data.metadata.key_base64}', this)">📋 Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ SAVE THIS KEY!</strong><br>
                    You need this key to decrypt your file. It's also in the metadata file.
                </div>
                
                <div class="download-buttons">
                    <a href="/download/${data.encrypted_file}" class="download-link">📥 Download Encrypted File</a>
                    <a href="/download/${data.metadata_file}" class="download-link">📥 Download Metadata</a>
                </div>
            `;
        } else {
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
        }
        resultDiv.style.display = 'block';
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
        resultDiv.style.display = 'block';
    } finally {
        setLoading(submitButton, false);
    }
});

// Copy to clipboard function
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = '✓ Copied!';
        button.style.backgroundColor = '#28a745';
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// Manual decryption form handler
document.getElementById('decryptManualForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const resultDiv = document.getElementById('decryptResult');
    const submitButton = this.querySelector('button[type="submit"]');
    
    setLoading(submitButton, true);
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch('/decrypt', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <h3>✅ Decryption Successful!</h3>
                <p><strong>Decrypted file:</strong> ${data.decrypted_file}</p>
                <a href="/download/${data.decrypted_file}" class="download-link">📥 Download Decrypted File</a>
            `;
        } else {
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
        }
        resultDiv.style.display = 'block';
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
        resultDiv.style.display = 'block';
    } finally {
        setLoading(submitButton, false);
    }
});

// Metadata decryption form handler
document.getElementById('decryptMetaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const resultDiv = document.getElementById('decryptResult');
    const submitButton = this.querySelector('button[type="submit"]');
    
    setLoading(submitButton, true);
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch('/decrypt', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <h3>✅ Decryption Successful!</h3>
                <p><strong>Decrypted file:</strong> ${data.decrypted_file}</p>
                <a href="/download/${data.decrypted_file}" class="download-link">📥 Download Decrypted File</a>
            `;
        } else {
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
        }
        resultDiv.style.display = 'block';
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
        resultDiv.style.display = 'block';
    } finally {
        setLoading(submitButton, false);
    }
});

// Clear results when switching tabs
document.querySelectorAll('.tablinks').forEach(button => {
    button.addEventListener('click', function() {
        document.getElementById('encryptResult').style.display = 'none';
        document.getElementById('decryptResult').style.display = 'none';
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('File Encryption Tool loaded');
});