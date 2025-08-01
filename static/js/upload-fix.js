// Fix pour le bouton upload - Version simplifiée
document.addEventListener('DOMContentLoaded', function() {
    console.log('Upload fix loaded');
    
    // Éléments principaux
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const chooseFileBtn = document.getElementById('chooseFileBtn');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    
    // Fix pour le bouton Choose File
    if (chooseFileBtn && fileInput) {
        chooseFileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fileInput.click();
        });
    }
    
    // Gestion de la sélection de fichier
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileSelection(file);
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
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });
    }
    
    function handleFileSelection(file) {
        if (!file) return;
        
        // Validation basique
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            alert('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
            return;
        }
        
        // Taille max 16MB
        if (file.size > 16 * 1024 * 1024) {
            alert('Fichier trop volumineux. Maximum 16MB.');
            return;
        }
        
        // Afficher les infos du fichier
        if (fileInfo) {
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileIcon = document.getElementById('fileIcon');
            
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatFileSize(file.size);
            
            // Icône selon le type
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
        
        // Activer le bouton de soumission
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        console.log('Fichier sélectionné:', file.name);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Fonction globale pour effacer le fichier
    window.clearFile = function() {
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
        console.log('Fichier effacé');
    };
});