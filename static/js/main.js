// AcadCheck - Main JavaScript File
console.log('\n   _____                _  _____ _               _    \n  |  _  |              | |/  __ \\ |             | |   \n  | | | |_ __   __ _  __| || /  \\/ |__   ___  ___| | __\n  | | | | \'_ \\ / _` |/ _` || |   | \'_ \\ / _ \\/ __| |/ /\n  \\ \\_/ / | | | (_| | (_| || \\__/\\ | | |  __/ (__|   < \n   \\___/|_| |_|\\__,_|\\__,_| \\____/_| |_|\\___|\\___|_|\\_\\\n\n  Academic Integrity Platform\n  Version 1.0.0');

console.log('AcadCheck application initialized');

// Upload functionality
document.addEventListener('DOMContentLoaded', function() {
    // File upload handlers
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    const uploadProgress = document.getElementById('uploadProgress');

    if (fileInput && dropZone) {
        // Drag and drop handlers
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        // File input change handler
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        // Choose file button handler
        const chooseFileBtn = document.getElementById('chooseFileBtn');
        if (chooseFileBtn) {
            chooseFileBtn.addEventListener('click', function() {
                fileInput.click();
            });
        }
    }

    // Handle file selection
    function handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain'
        ];

        if (!allowedTypes.includes(file.type)) {
            alert('Please select a valid file type (PDF, DOCX, TXT)');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            alert('File too large. Maximum size is 16MB.');
            return;
        }

        // Show file info
        if (fileInfo) {
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileIcon = document.getElementById('fileIcon');

            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatFileSize(file.size);
            
            // Update icon based on file type
            if (fileIcon) {
                fileIcon.className = 'fas fa-2x text-success me-3';
                if (file.type.includes('pdf')) {
                    fileIcon.classList.add('fa-file-pdf');
                } else if (file.type.includes('word')) {
                    fileIcon.classList.add('fa-file-word');
                } else {
                    fileIcon.classList.add('fa-file-alt');
                }
            }

            fileInfo.style.display = 'block';
        }

        // Enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
        }

        // Hide drop zone text
        const dropText = dropZone ? dropZone.querySelector('.text-muted') : null;
        if (dropText) {
            dropText.style.display = 'none';
        }
    }

    // Clear file function
    window.clearFile = function() {
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
        
        const dropText = dropZone ? dropZone.querySelector('.text-muted') : null;
        if (dropText) {
            dropText.style.display = 'block';
        }
    };

    // Form submission handler
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            if (uploadProgress) {
                uploadProgress.style.display = 'block';
            }
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            }
        });
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Fix parentheses balance
console.log('Main.js loaded correctly');