#!/usr/bin/env python3
"""
Script d'installation des dépendances pour éviter le problème sqlite3
"""
import subprocess
import sys

def install_package(package):
    """Installer un package individuellement"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de {package}: {e}")
        return False

def main():
    """Installer toutes les dépendances nécessaires"""
    packages = [
        "Flask==2.3.3",
        "Werkzeug==2.3.7", 
        "Jinja2==3.1.2",
        "pandas>=2.3.2",
        "openpyxl>=3.1.5",
        "requests>=2.32.5"
    ]
    
    print("🚀 Installation des dépendances TCA Visa System...")
    print("ℹ️  sqlite3 est intégré à Python, pas besoin de l'installer")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Résultat: {success_count}/{len(packages)} packages installés")
    
    if success_count == len(packages):
        print("✅ Toutes les dépendances sont installées!")
        print("🚀 Vous pouvez maintenant lancer: python app.py")
    else:
        print("⚠️  Certaines dépendances n'ont pas pu être installées")
        sys.exit(1)

if __name__ == "__main__":
    main()
