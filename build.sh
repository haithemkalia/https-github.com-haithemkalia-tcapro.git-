#!/bin/bash
# Script de build pour Vercel

echo "🚀 Début du build Vercel..."

# Installer les dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r requirements-deploy.txt

# Installer les dépendances Node.js
echo "📦 Installation des dépendances Node.js..."
npm install

# Compiler les assets
echo "🏗️ Compilation des assets..."
npm run build

echo "✅ Build terminé avec succès !"