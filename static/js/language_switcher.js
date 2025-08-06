/**
 * Système de changement de langue dynamique pour AcadCheck
 */

class LanguageSwitcher {
    constructor() {
        this.currentLanguage = document.documentElement.lang || 'fr';
        this.init();
    }

    init() {
        // Écouter les clics sur les liens de changement de langue
        const languageLinks = document.querySelectorAll('a[href*="/set-language/"]');
        languageLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const language = link.href.split('/set-language/')[1];
                this.switchLanguage(language);
            });
        });

        // Détecter le changement de langue automatique via URL
        this.detectLanguageFromURL();
    }

    switchLanguage(newLanguage) {
        if (newLanguage === this.currentLanguage) {
            return;
        }

        // Afficher un indicateur de chargement
        this.showLoadingIndicator();

        // Faire la requête de changement de langue
        fetch(`/set-language/${newLanguage}`, {
            method: 'GET',
            headers: {
                'Accept': 'text/html',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                // Recharger la page pour appliquer la nouvelle langue
                window.location.reload();
            } else {
                throw new Error('Erreur lors du changement de langue');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            this.hideLoadingIndicator();
            
            // Afficher un message d'erreur
            this.showMessage('Erreur lors du changement de langue', 'error');
        });
    }

    detectLanguageFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const lang = urlParams.get('lang');
        
        if (lang && lang !== this.currentLanguage) {
            this.currentLanguage = lang;
            document.documentElement.lang = lang;
        }
    }

    showLoadingIndicator() {
        // Créer un indicateur de chargement discret
        const indicator = document.createElement('div');
        indicator.id = 'language-loading';
        indicator.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <small>Changement de langue...</small>
            </div>
        `;
        indicator.className = 'position-fixed top-0 end-0 m-3 alert alert-info alert-dismissible';
        indicator.style.zIndex = '9999';
        
        document.body.appendChild(indicator);
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('language-loading');
        if (indicator) {
            indicator.remove();
        }
    }

    showMessage(message, type = 'info') {
        // Créer un message temporaire
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insérer après la navigation
        const nav = document.querySelector('nav');
        if (nav) {
            nav.insertAdjacentElement('afterend', alert);
        }
        
        // Supprimer automatiquement après 5 secondes
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    // Méthode utilitaire pour obtenir la langue actuelle
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Méthode pour mettre à jour la langue depuis l'extérieur
    setCurrentLanguage(language) {
        this.currentLanguage = language;
        document.documentElement.lang = language;
    }
}

// Initialiser le changeur de langue quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    window.languageSwitcher = new LanguageSwitcher();
    
    // Logs de débogage
    console.log(`🌍 Language Switcher initialisé - Langue: ${window.languageSwitcher.getCurrentLanguage()}`);
});