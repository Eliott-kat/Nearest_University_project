// Solution optimisée pour upload sans double-clic
console.log('Upload simple chargé');

let isFileSelected = false;
let fileInputBound = false;

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUpload);
} else {
    initUpload();
}

function initUpload() {
    const chooseBtn = document.getElementById('chooseFileBtn');
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    
    if (chooseBtn && fileInput && !fileInputBound) {
        // Marquer comme lié pour éviter les duplications
        fileInputBound = true;
        
        // Supprimer TOUS les anciens événements
        chooseBtn.replaceWith(chooseBtn.cloneNode(true));
        const newChooseBtn = document.getElementById('chooseFileBtn');
        
        // Event listener unique pour le bouton
        newChooseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!isFileSelected) {
                fileInput.click();
            }
        });
        
        // Event listener unique pour le file input
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && !isFileSelected) {
                isFileSelected = true;
                showFileInfo(file);
                // Reset après traitement
                setTimeout(() => { isFileSelected = false; }, 500);
            }
        });
        
        console.log('Bouton Choose File configuré (unique)');
    }
    
    // Drag & Drop amélioré
    if (dropZone && fileInput) {
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                fileInput.files = files;
                showFileInfo(file);
            }
        });
    }
}

function showFileInfo(file) {
    // Validation du fichier
    if (!validateFile(file)) {
        return;
    }
    
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileIcon = document.getElementById('fileIcon');
    const submitBtn = document.getElementById('submitBtn');
    
    // Mise à jour des informations
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatSize(file.size);
    
    // Icône selon le type de fichier
    if (fileIcon) {
        fileIcon.className = 'fas fa-2x text-success me-3';
        if (file.name.toLowerCase().endsWith('.pdf')) {
            fileIcon.classList.add('fa-file-pdf');
        } else if (file.name.toLowerCase().endsWith('.docx') || file.name.toLowerCase().endsWith('.doc')) {
            fileIcon.classList.add('fa-file-word');
        } else {
            fileIcon.classList.add('fa-file-alt');
        }
    }
    
    // Afficher les informations et activer le bouton
    if (fileInfo) fileInfo.style.display = 'block';
    if (submitBtn) submitBtn.disabled = false;
    
    console.log('Fichier validé et affiché:', file.name);
}

function validateFile(file) {
    // Types autorisés
    const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain'
    ];
    
    const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        alert('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
        clearFile();
        return false;
    }
    
    // Taille max 16MB
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('Fichier trop volumineux. Maximum 16MB.');
        clearFile();
        return false;
    }
    
    // Nom de fichier valide
    if (file.name.length > 200) {
        alert('Nom de fichier trop long.');
        clearFile();
        return false;
    }
    
    return true;
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
    return Math.round(bytes / (1024 * 1024)) + ' MB';
}

function clearFile() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (submitBtn) submitBtn.disabled = true;
    
    // Reset du flag de sélection
    isFileSelected = false;
    
    console.log('Fichier supprimé');
}

// Fonction globale accessible depuis HTML
window.clearFile = clearFile;