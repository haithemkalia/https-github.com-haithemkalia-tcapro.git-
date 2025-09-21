# 🌐 Guide de Configuration Réseau - TCA Visa System

## 📋 Configuration pour Accès Multi-PC

### 🚀 Démarrage Rapide

1. **Sur le PC serveur principal :**
   ```bash
   python -X utf8 start_network_server.py
   ```

2. **Sur les autres PC du réseau :**
   - Ouvrir un navigateur web
   - Aller à l'adresse affichée (ex: `http://192.168.1.100:5000`)

### 🔧 Configuration Manuelle

Si vous préférez démarrer manuellement :

```bash
python -X utf8 app.py
```

L'application est déjà configurée avec `host='0.0.0.0'` pour l'accès réseau.

### 📱 URLs d'Accès

- **URL locale :** `http://localhost:5000` (PC serveur uniquement)
- **URL réseau :** `http://[IP_LOCALE]:5000` (tous les PC du réseau)
- **URL par nom :** `http://[NOM_PC]:5000` (si le DNS fonctionne)

### 🔍 Trouver l'Adresse IP

**Windows :**
```cmd
ipconfig
```

**Linux/Mac :**
```bash
ifconfig
```

### ⚠️ Vérifications Importantes

1. **Pare-feu Windows :**
   - Autoriser le port 5000
   - Ou désactiver temporairement le pare-feu

2. **Réseau :**
   - Tous les PC doivent être sur le même réseau
   - Vérifier la connectivité avec `ping [IP_SERVEUR]`

3. **Sécurité :**
   - L'application est accessible à tous sur le réseau
   - Considérez un VPN pour l'accès distant

### 🛠️ Dépannage

**Problème : "Connexion refusée"**
- Vérifier que le serveur est démarré
- Vérifier l'adresse IP
- Vérifier le pare-feu

**Problème : "Site inaccessible"**
- Vérifier la connectivité réseau
- Essayer l'IP au lieu du nom de PC
- Vérifier que le port 5000 est libre

### 📊 Fonctionnalités Multi-Utilisateur

✅ **Accès simultané :** Plusieurs PC peuvent accéder en même temps
✅ **Données partagées :** Toutes les modifications sont visibles en temps réel
✅ **Tri synchronisé :** L'ordre chronologique est maintenu pour tous
✅ **Recherche partagée :** Les filtres fonctionnent pour tous les utilisateurs

### 🔄 Redémarrage du Serveur

Pour redémarrer le serveur après des modifications :
1. Arrêter avec `Ctrl+C`
2. Relancer avec `python -X utf8 start_network_server.py`

### 📞 Support

En cas de problème, vérifiez :
1. L'adresse IP affichée au démarrage
2. La connectivité réseau entre les PC
3. Les paramètres du pare-feu
4. Que le port 5000 n'est pas utilisé par une autre application
