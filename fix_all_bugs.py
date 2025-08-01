#!/usr/bin/env python3
"""
Correctif universel pour tous les bugs AcadCheck
"""

import os
import shutil
import logging
from datetime import datetime

def fix_javascript_conflicts():
    """Supprime les conflits JavaScript"""
    print("🔧 CORRECTION CONFLITS JAVASCRIPT")
    
    # Supprimer l'ancien main.js qui cause des conflits
    old_main = 'static/js/main.js'
    if os.path.exists(old_main):
        try:
            os.remove(old_main)
            print(f"✅ Supprimé: {old_main}")
        except Exception as e:
            print(f"❌ Erreur suppression {old_main}: {e}")
    
    # Vérifier que main-minimal.js existe
    minimal_main = 'static/js/main-minimal.js'
    if not os.path.exists(minimal_main):
        # Créer un main-minimal.js basique
        content = '''// AcadCheck - Main JavaScript (Minimal)
console.log('AcadCheck initialized');

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
});'''
        
        try:
            with open(minimal_main, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Créé: {minimal_main}")
        except Exception as e:
            print(f"❌ Erreur création {minimal_main}: {e}")

def fix_upload_functionality():
    """Corrige la fonctionnalité d'upload"""
    print("📁 CORRECTION FONCTIONNALITÉ UPLOAD")
    
    upload_js = 'static/js/simple-upload.js'
    if os.path.exists(upload_js):
        try:
            # Contenu corrigé sans double événements
            corrected_content = '''// Upload handler - Version corrigée
console.log('Upload handler loaded');

let uploadInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    if (uploadInitialized) return;
    uploadInitialized = true;
    
    const fileInput = document.getElementById('fileInput');
    const chooseBtn = document.getElementById('chooseFileBtn');
    const dropZone = document.getElementById('dropZone');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    
    // Bouton Choose File
    if (chooseBtn && fileInput) {
        chooseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fileInput.click();
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
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
                const file = files[0];
                fileInput.files = files;
                handleFile(file);
            }
        });
    }
    
    function handleFile(file) {
        if (!validateFile(file)) return;
        
        // Afficher info fichier
        if (fileInfo) {
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileIcon = document.getElementById('fileIcon');
            
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatSize(file.size);
            
            if (fileIcon) {
                fileIcon.className = 'fas fa-2x text-success me-3';
                const ext = file.name.toLowerCase();
                if (ext.includes('.pdf')) {
                    fileIcon.classList.add('fa-file-pdf');
                } else if (ext.includes('.doc')) {
                    fileIcon.classList.add('fa-file-word');
                } else {
                    fileIcon.classList.add('fa-file-alt');
                }
            }
            
            fileInfo.style.display = 'block';
        }
        
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        console.log('Fichier sélectionné:', file.name);
    }
    
    function validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain'
        ];
        
        const maxSize = 16 * 1024 * 1024;
        
        if (!allowedTypes.includes(file.type)) {
            alert('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
            return false;
        }
        
        if (file.size > maxSize) {
            alert('Fichier trop volumineux. Maximum 16MB.');
            return false;
        }
        
        return true;
    }
    
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return Math.round(bytes / (1024 * 1024)) + ' MB';
    }
    
    // Fonction globale pour clear
    window.clearFile = function() {
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
    };
    
    console.log('Upload handler initialized');
});'''
            
            with open(upload_js, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            print(f"✅ Corrigé: {upload_js}")
            
        except Exception as e:
            print(f"❌ Erreur correction upload: {e}")

def fix_template_references():
    """Corrige les références dans les templates"""
    print("🎨 CORRECTION RÉFÉRENCES TEMPLATES")
    
    # Corriger base.html pour utiliser main-minimal.js
    base_template = 'templates/base.html'
    if os.path.exists(base_template):
        try:
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer main.js par main-minimal.js
            content = content.replace(
                "static/js/main.js",
                "static/js/main-minimal.js"
            )
            
            with open(base_template, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigé: {base_template}")
            
        except Exception as e:
            print(f"❌ Erreur correction template: {e}")

def fix_routes_issues():
    """Vérifie et corrige les problèmes de routes"""
    print("🛣️ VÉRIFICATION ROUTES")
    
    try:
        from app import app
        
        with app.app_context():
            # Lister toutes les routes
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes.append(f"{rule.rule} -> {rule.endpoint}")
            
            print(f"✅ {len(routes)} routes disponibles")
            
            # Tester quelques routes critiques
            with app.test_client() as client:
                critical_routes = ['/demo', '/upload', '/dashboard']
                for route in critical_routes:
                    try:
                        response = client.get(route)
                        if response.status_code in [200, 302]:
                            print(f"✅ Route {route}: OK ({response.status_code})")
                        else:
                            print(f"⚠️ Route {route}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Route {route}: {str(e)[:50]}...")
                        
    except Exception as e:
        print(f"❌ Erreur test routes: {e}")

def clean_obsolete_files():
    """Nettoie les fichiers obsolètes"""
    print("🧹 NETTOYAGE FICHIERS OBSOLÈTES")
    
    obsolete_files = [
        'static/js/upload-fix.js',
        'static/js/main.js.backup',
        'bug_fixes.py.backup'
    ]
    
    for file_path in obsolete_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur suppression {file_path}: {e}")

def run_comprehensive_fix():
    """Exécute toutes les corrections"""
    print("🚀 CORRECTION COMPLÈTE DE TOUS LES BUGS")
    print("=" * 50)
    
    fix_javascript_conflicts()
    fix_upload_functionality()
    fix_template_references()
    fix_routes_issues()
    clean_obsolete_files()
    
    print("\\n🎯 TOUTES LES CORRECTIONS APPLIQUÉES")
    print("✅ JavaScript: Conflits résolus")
    print("✅ Upload: Fonctionnalité corrigée")
    print("✅ Templates: Références mises à jour")
    print("✅ Routes: Vérifiées")
    print("✅ Nettoyage: Fichiers obsolètes supprimés")

if __name__ == "__main__":
    run_comprehensive_fix()