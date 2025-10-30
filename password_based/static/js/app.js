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
        button.innerHTML = '<span class="loading">Processing...</span>';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || button.textContent;
    }
}

// Encryption form handler
document.getElementById('encryptForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const resultDiv = document.getElementById('encryptResult');
    const submitButton = this.querySelector('button[type="submit"]');
    
    // Store original button text
    submitButton.setAttribute('data-original-text', submitButton.textContent);
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
                <h3>Encryption Successful!</h3>
                <p><strong>Encrypted file:</strong> ${data.encrypted_file}</p>
                <p><strong>Metadata file:</strong> ${data.metadata_file}</p>
                <div class="download-buttons">
                    <a href="/download/${data.encrypted_file}" class="download-link">Download Encrypted File</a>
                    <a href="/download/${data.metadata_file}" class="download-link">Download Metadata File</a>
                </div>
                <p class="warning"><strong>⚠️ Keep your password safe! You'll need it for decryption.</strong></p>
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

// Manual decryption form handler
document.getElementById('decryptManualForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const resultDiv = document.getElementById('decryptResult');
    const submitButton = this.querySelector('button[type="submit"]');
    
    submitButton.setAttribute('data-original-text', submitButton.textContent);
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
                <h3>Decryption Successful!</h3>
                <p><strong>Decrypted file:</strong> ${data.decrypted_file}</p>
                <a href="/download/${data.decrypted_file}" class="download-link">Download Decrypted File</a>
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
    
    submitButton.setAttribute('data-original-text', submitButton.textContent);
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
                <h3>Decryption Successful!</h3>
                <p><strong>Decrypted file:</strong> ${data.decrypted_file}</p>
                <a href="/download/${data.decrypted_file}" class="download-link">Download Decrypted File</a>
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

// Add some CSS for loading state
const style = document.createElement('style');
style.textContent = `
    .loading {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .download-buttons {
        margin: 15px 0;
    }
    .warning {
        margin-top: 15px;
        padding: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
        color: #856404;
    }
`;
document.head.appendChild(style);

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('File Encryption Tool loaded successfully');
});