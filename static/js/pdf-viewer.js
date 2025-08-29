document.addEventListener('DOMContentLoaded', function() {
    const pdfUrl = document.getElementById('pdf-viewer').getAttribute('data-pdf-url');
    const pdfContainer = document.getElementById('pdf-viewer');
    const textView = document.getElementById('text-view');
    const pdfView = document.getElementById('pdf-view');
    const toggleTextBtn = document.getElementById('toggle-text-view');
    const togglePdfBtn = document.getElementById('toggle-pdf-view');

    toggleTextBtn.addEventListener('click', function() {
        textView.style.display = 'block';
        pdfView.style.display = 'none';
        toggleTextBtn.classList.add('active');
        togglePdfBtn.classList.remove('active');
    });

    togglePdfBtn.addEventListener('click', function() {
        textView.style.display = 'none';
        pdfView.style.display = 'block';
        togglePdfBtn.classList.add('active');
        toggleTextBtn.classList.remove('active');
        loadPdf();
    });

    function loadPdf() {
        if (pdfContainer.getAttribute('data-loaded') === 'true') {
            return;
        }
        pdfContainer.setAttribute('data-loaded', 'true');

        // Load PDF.js library
        if (typeof pdfjsLib === 'undefined') {
            const script = document.createElement('script');
            script.src = '/static/js/pdfjs/pdf.js';
            script.onload = () => {
                renderPdf();
            };
            document.head.appendChild(script);
        } else {
            renderPdf();
        }
    }

    function renderPdf() {
        // This is a placeholder for actual PDF.js rendering logic.
        // For now, just show a message.
        pdfView.innerHTML = '<p>PDF.js viewer would render the PDF here: <a href="' + pdfUrl + '" target="_blank">Open PDF</a></p>';
    }

    // Initialize with text view visible
    toggleTextBtn.click();
});
