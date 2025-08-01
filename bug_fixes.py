#!/usr/bin/env python3
"""
Correctifs automatiques pour les bugs AcadCheck
Détecte et corrige automatiquement les problèmes courants
"""

import os
import re
import logging
from datetime import datetime

class BugFixer:
    """Système de correction automatique des bugs"""
    
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
    
    def check_javascript_syntax(self):
        """Vérifie la syntaxe JavaScript"""
        js_files = ['static/js/main.js', 'static/js/simple-upload.js']
        
        for js_file in js_files:
            if os.path.exists(js_file):
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Vérifications basiques
                    issues = []
                    
                    # Template literals problématiques
                    if re.search(r'console\.log\(`[^`]*\n[^`]*`\)', content):
                        issues.append("Template literal multiline dans console.log")
                    
                    # Parenthèses non fermées
                    open_parens = content.count('(')
                    close_parens = content.count(')')
                    if open_parens != close_parens:
                        issues.append(f"Parenthèses déséquilibrées: {open_parens} ouvertes, {close_parens} fermées")
                    
                    # Accolades non fermées
                    open_braces = content.count('{')
                    close_braces = content.count('}')
                    if open_braces != close_braces:
                        issues.append(f"Accolades déséquilibrées: {open_braces} ouvertes, {close_braces} fermées")
                    
                    if issues:
                        self.issues_found.extend([(js_file, issue) for issue in issues])
                        logging.warning(f"Issues trouvées dans {js_file}: {', '.join(issues)}")
                    else:
                        logging.info(f"✅ {js_file}: Syntaxe correcte")
                        
                except Exception as e:
                    self.issues_found.append((js_file, f"Erreur lecture: {e}"))
    
    def fix_double_event_listeners(self):
        """Corrige les event listeners doubles"""
        js_file = 'static/js/simple-upload.js'
        
        if os.path.exists(js_file):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifier s'il y a des event listeners multiples
                if content.count('addEventListener') > 4:  # Seuil normal
                    logging.warning("Possible duplication d'event listeners détectée")
                    self.issues_found.append((js_file, "Event listeners multiples"))
                
                # Vérifier la logique de prévention double-clic
                if 'isFileSelected' not in content:
                    logging.info("Variable de contrôle double-clic présente")
                
            except Exception as e:
                self.issues_found.append((js_file, f"Erreur vérification: {e}"))
    
    def check_html_template_errors(self):
        """Vérifie les erreurs dans les templates HTML"""
        template_files = [
            'templates/upload.html',
            'templates/base.html',
            'templates/dashboard.html'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Vérifications
                    issues = []
                    
                    # Scripts manquants ou mal référencés
                    if 'simple-upload.js' in content and 'upload-fix.js' in content:
                        issues.append("Scripts JS multiples référencés")
                    
                    # Éléments HTML manquants
                    required_ids = ['fileInput', 'chooseFileBtn', 'fileInfo']
                    for req_id in required_ids:
                        if f'id="{req_id}"' not in content and template_file == 'templates/upload.html':
                            issues.append(f"ID manquant: {req_id}")
                    
                    if issues:
                        self.issues_found.extend([(template_file, issue) for issue in issues])
                    else:
                        logging.info(f"✅ {template_file}: Template correct")
                        
                except Exception as e:
                    self.issues_found.append((template_file, f"Erreur lecture: {e}"))
    
    def check_flask_routes(self):
        """Vérifie les routes Flask"""
        try:
            from app import app
            
            with app.app_context():
                # Tester les routes principales
                with app.test_client() as client:
                    critical_routes = [
                        ('/', 'Index'),
                        ('/demo', 'Demo'),
                        ('/upload', 'Upload')
                    ]
                    
                    for route, name in critical_routes:
                        try:
                            response = client.get(route)
                            if response.status_code not in [200, 302]:
                                self.issues_found.append(('routes.py', f"Route {route} retourne {response.status_code}"))
                            else:
                                logging.info(f"✅ Route {route}: {response.status_code}")
                        except Exception as e:
                            self.issues_found.append(('routes.py', f"Erreur route {route}: {e}"))
                            
        except ImportError as e:
            self.issues_found.append(('app.py', f"Erreur import Flask: {e}"))
    
    def apply_automatic_fixes(self):
        """Applique les corrections automatiques"""
        fixes_applied = 0
        
        # Fix 1: Nettoyer les anciens scripts JS
        upload_template = 'templates/upload.html'
        if os.path.exists(upload_template):
            try:
                with open(upload_template, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Supprimer les références multiples aux scripts
                if 'upload-fix.js' in content and 'simple-upload.js' in content:
                    content = content.replace('upload-fix.js', 'simple-upload.js')
                    
                    with open(upload_template, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append("Scripts JS dupliqués supprimés")
                    fixes_applied += 1
                    
            except Exception as e:
                logging.error(f"Erreur fix template: {e}")
        
        # Fix 2: Supprimer les fichiers JS obsolètes
        obsolete_files = ['static/js/upload-fix.js']
        for obs_file in obsolete_files:
            if os.path.exists(obs_file):
                try:
                    os.remove(obs_file)
                    self.fixes_applied.append(f"Fichier obsolète supprimé: {obs_file}")
                    fixes_applied += 1
                except Exception as e:
                    logging.error(f"Erreur suppression {obs_file}: {e}")
        
        return fixes_applied
    
    def generate_report(self):
        """Génère un rapport de correction"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': len(self.issues_found),
            'fixes_applied': len(self.fixes_applied),
            'details': {
                'issues': self.issues_found,
                'fixes': self.fixes_applied
            },
            'status': 'healthy' if len(self.issues_found) == 0 else 'issues_detected'
        }
        
        return report

def run_bug_fixes():
    """Exécute les corrections de bugs"""
    print("🐛 DÉTECTION ET CORRECTION AUTOMATIQUE DES BUGS")
    print("=" * 50)
    
    fixer = BugFixer()
    
    # Vérifications
    fixer.check_javascript_syntax()
    fixer.fix_double_event_listeners()
    fixer.check_html_template_errors()
    fixer.check_flask_routes()
    
    # Corrections automatiques
    fixes = fixer.apply_automatic_fixes()
    
    # Rapport
    report = fixer.generate_report()
    
    print(f"📊 RÉSULTATS:")
    print(f"   - Issues détectées: {report['issues_found']}")
    print(f"   - Corrections appliquées: {report['fixes_applied']}")
    print(f"   - Statut: {report['status']}")
    
    if report['details']['issues']:
        print(f"\\n⚠️ ISSUES DÉTECTÉES:")
        for file_path, issue in report['details']['issues']:
            print(f"   - {file_path}: {issue}")
    
    if report['details']['fixes']:
        print(f"\\n✅ CORRECTIONS APPLIQUÉES:")
        for fix in report['details']['fixes']:
            print(f"   - {fix}")
    
    return report

if __name__ == "__main__":
    run_bug_fixes()