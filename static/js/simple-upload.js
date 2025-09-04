// Upload handler - Version corrigée
console.log('Upload handler loaded');

let uploadInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    if (uploadInitialized) return;
    uploadInitialized = true;
    
    const fileInput = document.getElementById('fileInput');
    const chooseBtn = document.getElementById('chooseFileBtn');
    const dropZone = document.getElementById('dropZone');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    
    // Bouton Choose File
    if (chooseBtn && fileInput) {
        chooseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fileInput.click();
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
            }
        });
    }
    
    // Drag & Drop
    if (dropZone) {
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
                const file = files[0];
                fileInput.files = files;
                handleFile(file);
            }
        });
    }
    
    function handleFile(file) {
        if (!validateFile(file)) return;

        // Hide drop zone
        if (dropZone) {
            dropZone.style.display = 'none';
        }

        // Afficher info fichier
        if (fileInfo) {
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileIcon = document.getElementById('fileIcon');

            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatSize(file.size);

            if (fileIcon) {
                fileIcon.className = 'fas fa-2x text-success me-3';
                const ext = file.name.toLowerCase();
                if (ext.includes('.pdf')) {
                    fileIcon.classList.add('fa-file-pdf');
                } else if (ext.includes('.doc')) {
                    fileIcon.classList.add('fa-file-word');
                } else {
                    fileIcon.classList.add('fa-file-alt');
                }
            }

            fileInfo.style.display = 'block';
        }

        if (submitBtn) {
            submitBtn.disabled = false;
        }

        console.log('Fichier sélectionné:', file.name);
    }
    
    function validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain'
        ];
        
        const maxSize = 16 * 1024 * 1024;
        
        if (!allowedTypes.includes(file.type)) {
            alert('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
            return false;
        }
        
        if (file.size > maxSize) {
            alert('Fichier trop volumineux. Maximum 16MB.');
            return false;
        }
        
        return true;
    }
    
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return Math.round(bytes / (1024 * 1024)) + ' MB';
    }
    
    // Fonction globale pour clear
    window.clearFile = function() {
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (submitBtn) submitBtn.disabled = true;
    if (dropZone) dropZone.style.display = '';
    };
    
    console.log('Upload handler initialized');
});