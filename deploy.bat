@echo off
echo 🚀 Déploiement TCA Visa System
echo ================================

echo 📦 Installation des dépendances...
python install-deps.py

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo 🔧 Configuration pour Vercel...
copy requirements-deploy.txt requirements.txt

echo 🌐 Déploiement sur Vercel...
vercel --prod

echo ✅ Déploiement terminé!
pause
