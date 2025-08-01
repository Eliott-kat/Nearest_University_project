// AcadCheck - Main JavaScript File (Minimal Version)
console.log('\n   _____                _  _____ _               _    \n  |  _  |              | |/  __ \\ |             | |   \n  | | | |_ __   __ _  __| || /  \\/ |__   ___  ___| | __\n  | | | | \'_ \\ / _` |/ _` || |   | \'_ \\ / _ \\/ __| |/ /\n  \\ \\_/ / | | | (_| | (_| || \\__/\\ | | |  __/ (__|   < \n   \\___/|_| |_|\\__,_|\\__,_| \\____/_| |_|\\___|\\___|_|\\_\\\n\n  Academic Integrity Platform\n  Version 1.0.0');

console.log('AcadCheck application initialized');

// Only alerts functionality - NO upload handlers to avoid conflicts
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    console.log('Main.js loaded correctly - alerts only');
});