// Solution simple pour bouton upload
console.log('Upload simple chargé');

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUpload);
} else {
    initUpload();
}

function initUpload() {
    // Bouton Choose File
    const chooseBtn = document.getElementById('chooseFileBtn');
    const fileInput = document.getElementById('fileInput');
    
    if (chooseBtn && fileInput) {
        chooseBtn.onclick = function() {
            fileInput.click();
        };
        console.log('Bouton Choose File configuré');
    }
    
    // Affichage du fichier sélectionné
    if (fileInput) {
        fileInput.onchange = function() {
            const file = this.files[0];
            if (file) {
                showFileInfo(file);
            }
        };
    }
}

function showFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const submitBtn = document.getElementById('submitBtn');
    
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatSize(file.size);
    if (fileInfo) fileInfo.style.display = 'block';
    if (submitBtn) submitBtn.disabled = false;
    
    console.log('Fichier sélectionné:', file.name);
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
    
    console.log('Fichier supprimé');
}