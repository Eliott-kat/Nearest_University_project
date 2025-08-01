
// Script pour forcer l'affichage des icônes Font Awesome
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Vérification icônes Font Awesome...');
    
    // Vérifier si Font Awesome est chargé
    const testIcon = document.createElement('i');
    testIcon.className = 'fas fa-check';
    testIcon.style.position = 'absolute';
    testIcon.style.left = '-9999px';
    document.body.appendChild(testIcon);
    
    const computedStyle = window.getComputedStyle(testIcon, '::before');
    const fontFamily = computedStyle.getPropertyValue('font-family');
    
    if (fontFamily.includes('Font Awesome')) {
        console.log('✅ Font Awesome chargé correctement');
    } else {
        console.log('❌ Font Awesome non chargé, application du fallback...');
        
        // Appliquer fallback emoji pour chaque icône
        const iconMap = {
            'fa-file-alt': '📄',
            'fa-check-circle': '✅', 
            'fa-clock': '⏰',
            'fa-chart-line': '📊',
            'fa-users': '👥',
            'fa-upload': '📤',
            'fa-download': '📥',
            'fa-history': '📜'
        };
        
        Object.keys(iconMap).forEach(iconClass => {
            const icons = document.querySelectorAll('.fas.' + iconClass);
            icons.forEach(icon => {
                icon.innerHTML = iconMap[iconClass];
                icon.style.fontFamily = 'Arial, sans-serif';
                icon.style.fontSize = '1.5rem';
            });
        });
    }
    
    document.body.removeChild(testIcon);
});
