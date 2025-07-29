"""
Module pour afficher clairement quel service de détection est utilisé
"""

def get_provider_display_name(provider_used):
    """Retourne le nom d'affichage du fournisseur utilisé"""
    provider_names = {
        'copyleaks': '🔍 Copyleaks (Priorité 1)',
        'plagiarismcheck': '🔄 PlagiarismCheck (Fallback)',
        'turnitin_local': '🏠 Algorithme Local Turnitin-Style',
        'none': '❌ Aucun service disponible'
    }
    return provider_names.get(provider_used, f'⚠️ Service inconnu: {provider_used}')

def get_provider_status_badge(provider_used, score):
    """Retourne un badge de statut pour l'affichage"""
    if provider_used == 'copyleaks':
        color = 'primary'
        icon = '🔍'
    elif provider_used == 'plagiarismcheck':
        color = 'warning'
        icon = '🔄'
    elif provider_used == 'turnitin_local':
        color = 'info'
        icon = '🏠'
    else:
        color = 'secondary'
        icon = '❓'
    
    return {
        'color': color,
        'icon': icon,
        'text': get_provider_display_name(provider_used),
        'score': f'{score}%'
    }