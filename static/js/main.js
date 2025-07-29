// AcadCheck - Academic Integrity Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFileUpload();
    initializeTooltips();
    initializeProgressBars();
    initializeAnimations();
    initializeNavigation();
    initializeDataTables();
    
    console.log('AcadCheck application initialized');
});

// File Upload Enhancement
function initializeFileUpload() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(dropZone => {
        const fileInput = dropZone.querySelector('input[type="file"]') || 
                         document.querySelector('input[type="file"]');
        
        if (!fileInput) return;
        
        // Drag and drop events
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);
        
        // Click to upload - only if clicking on the dropzone itself, not buttons
        dropZone.addEventListener('click', function(e) {
            if (e.target.type !== 'file' && !e.target.closest('button') && e.target === dropZone) {
                fileInput.click();
            }
        });
        
        // Handle choose file button
        const chooseFileBtn = document.getElementById('chooseFileBtn');
        if (chooseFileBtn) {
            chooseFileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                fileInput.click();
            });
        }
        
        // File input change
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileSelect(this.files[0]);
            }
        });
    });
    
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
        this.style.borderColor = '#0d6efd';
        this.style.backgroundColor = '#e7f1ff';
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        this.style.borderColor = '#dee2e6';
        this.style.backgroundColor = '#f8f9fa';
    }
    
    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        this.style.borderColor = '#dee2e6';
        this.style.backgroundColor = '#f8f9fa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    }
    
    function handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        const allowedExtensions = ['.pdf', '.docx', '.txt'];
        
        const isValidType = allowedTypes.includes(file.type) || 
                           allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValidType) {
            showNotification('Please upload a PDF, DOCX, or TXT file.', 'error');
            return;
        }
        
        // Validate file size (16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            showNotification('File size must be less than 16MB.', 'error');
            return;
        }
        
        // Update file input
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        }
        
        // Show file information
        displayFileInfo(file);
        
        // Enable submit button
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.add('fade-in');
        }
    }
    
    function displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = document.getElementById('fileIcon');
        
        if (!fileInfo || !fileName || !fileSize || !fileIcon) return;
        
        // Update file information
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Set appropriate icon
        if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
            fileIcon.className = 'fas fa-file-pdf fa-2x text-danger me-3';
        } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                   file.name.toLowerCase().endsWith('.docx')) {
            fileIcon.className = 'fas fa-file-word fa-2x text-primary me-3';
        } else {
            fileIcon.className = 'fas fa-file-alt fa-2x text-secondary me-3';
        }
        
        // Show file info with animation
        fileInfo.style.display = 'block';
        fileInfo.classList.add('slide-up');
    }
}

// Clear file function (global for button onclick)
function clearFile() {
    const fileInput = document.querySelector('input[type="file"]');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (submitBtn) submitBtn.disabled = true;
}

// File size formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Tooltip initialization
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add tooltips to highlighted text
    const highlightedElements = document.querySelectorAll('.highlight-plagiarism, .highlight-ai, .highlight-both');
    highlightedElements.forEach(element => {
        if (!element.hasAttribute('title')) {
            const type = element.classList.contains('highlight-plagiarism') ? 'Plagiarism' : 
                        element.classList.contains('highlight-ai') ? 'AI Generated' : 'Both Issues';
            element.setAttribute('title', `${type} detected in this text segment`);
            element.setAttribute('data-bs-toggle', 'tooltip');
            element.setAttribute('data-bs-placement', 'top');
            new bootstrap.Tooltip(element);
        }
    });
}

// Progress bar animations
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        // Animate to target width
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });
}

// Page animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.card, .feature-card, .stats-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// Navigation enhancements
function initializeNavigation() {
    // Active page highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Data table enhancements
function initializeDataTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // Add hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(13, 110, 253, 0.04)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        // Add sorting capability (basic)
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this);
            });
        });
    });
}

// Table sorting function
function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.classList.contains('sort-asc');
    
    // Remove existing sort classes
    header.parentNode.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add new sort class
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? bNum - aNum : aNum - bNum;
        } else {
            return isAscending ? bValue.localeCompare(aValue) : aValue.localeCompare(bValue);
        }
    });
    
    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 150);
        }
    }, duration);
}

// Form submission handling
document.addEventListener('submit', function(e) {
    const form = e.target;
    
    if (form.id === 'uploadForm') {
        const fileInput = form.querySelector('input[type="file"]');
        const submitBtn = form.querySelector('#submitBtn');
        const uploadProgress = form.querySelector('#uploadProgress');
        
        if (!fileInput || !fileInput.files.length) {
            e.preventDefault();
            showNotification('Please select a file to upload.', 'warning');
            return;
        }
        
        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
        }
        
        if (uploadProgress) {
            uploadProgress.style.display = 'block';
            uploadProgress.classList.add('slide-up');
        }
    }
});

// Auto-refresh for processing documents
function checkProcessingDocuments() {
    const processingElements = document.querySelectorAll('.spinner-border');
    
    if (processingElements.length > 0) {
        // Refresh page every 30 seconds if there are processing documents
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    }
}

// Initialize processing check
setTimeout(checkProcessingDocuments, 1000);

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showNotification('Failed to copy text', 'error');
    });
}

// Print report function
function printReport() {
    window.print();
}

// Download functionality enhancement
function enhanceDownloadLinks() {
    const downloadLinks = document.querySelectorAll('a[href*="download"]');
    
    downloadLinks.forEach(link => {
        link.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                const originalClass = icon.className;
                icon.className = 'fas fa-spinner fa-spin';
                
                setTimeout(() => {
                    icon.className = originalClass;
                    showNotification('Download started!', 'success', 2000);
                }, 1000);
            }
        });
    });
}

// Initialize download enhancements
setTimeout(enhanceDownloadLinks, 1000);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+U for upload (when not in input field)
    if (e.ctrlKey && e.key === 'u' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
        const uploadBtn = document.querySelector('a[href*="upload"]');
        if (uploadBtn) {
            window.location.href = uploadBtn.href;
        }
    }
    
    // Escape to clear modals or notifications
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        });
    }
});

// Responsive table handling
function makeTablesResponsive() {
    const tables = document.querySelectorAll('.table:not(.table-responsive *)');
    
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialize responsive tables
setTimeout(makeTablesResponsive, 500);

// Search functionality for tables
function addTableSearch() {
    const tables = document.querySelectorAll('table[data-searchable]');
    
    tables.forEach(table => {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Search documents...';
        
        table.parentNode.insertBefore(searchInput, table);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    });
}

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.style.display = 'none';
        console.warn('Failed to load image:', e.target.src);
    }
}, true);

// Back to top button
function addBackToTopButton() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary position-fixed';
    backToTop.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(backToTop);
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.style.display = 'flex';
            backToTop.style.alignItems = 'center';
            backToTop.style.justifyContent = 'center';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

// Initialize back to top button
setTimeout(addBackToTopButton, 1000);

// Console branding
console.log(`
   _____                _  _____ _               _    
  |  _  |              | |/  __ \\ |             | |   
  | | | |_ __   __ _  __| || /  \\/ |__   ___  ___| | __
  | | | | '_ \\ / _\` |/ _\` || |   | '_ \\ / _ \\/ __| |/ /
  \\ \\_/ / | | | (_| | (_| || \\__/\\ | | |  __/ (__|   < 
   \\___/|_| |_|\\__,_|\\__,_| \\____/_| |_|\\___|\\___|_|\\_\\

  Academic Integrity Platform
  Version 1.0.0
`);
