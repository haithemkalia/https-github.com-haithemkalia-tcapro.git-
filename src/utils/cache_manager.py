#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de cache pour améliorer les performances du système TCA
"""

import time
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class CacheManager:
    """Gestionnaire de cache en mémoire pour les données fréquemment utilisées"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 minutes par défaut
        
    def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        
        # Vérifier si le cache a expiré
        if time.time() > cache_entry['expires_at']:
            del self._cache[key]
            return None
            
        cache_entry['last_accessed'] = time.time()
        return cache_entry['data']
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Stocker une valeur dans le cache"""
        if ttl is None:
            ttl = self._default_ttl
            
        self._cache[key] = {
            'data': data,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'last_accessed': time.time(),
            'ttl': ttl
        }
    
    def delete(self, key: str) -> bool:
        """Supprimer une entrée du cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Vider tout le cache"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Nettoyer les entrées expirées et retourner le nombre d'entrées supprimées"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time > entry['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du cache"""
        current_time = time.time()
        total_entries = len(self._cache)
        expired_entries = 0
        
        for entry in self._cache.values():
            if current_time > entry['expires_at']:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'cache_keys': list(self._cache.keys())
        }
    
    def has_key(self, key: str) -> bool:
        """Vérifier si une clé existe et n'est pas expirée"""
        if key not in self._cache:
            return False
            
        if time.time() > self._cache[key]['expires_at']:
            del self._cache[key]
            return False
            
        return True

# Instance globale du cache
cache_manager = CacheManager()

# Fonctions utilitaires pour le cache
def cache_statistics(func):
    """Décorateur pour mettre en cache les statistiques"""
    def wrapper(*args, **kwargs):
        cache_key = f"stats_{func.__name__}_{hash(str(args) + str(kwargs))}"
        
        # Essayer de récupérer depuis le cache
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            print(f"📊 Statistiques récupérées depuis le cache: {func.__name__}")
            return cached_result
        
        # Calculer et mettre en cache
        result = func(*args, **kwargs)
        cache_manager.set(cache_key, result, ttl=180)  # 3 minutes pour les stats
        print(f"📊 Statistiques calculées et mises en cache: {func.__name__}")
        
        return result
    
    return wrapper

def cache_client_data(func):
    """Décorateur pour mettre en cache les données clients"""
    def wrapper(*args, **kwargs):
        # Créer une clé de cache basée sur les arguments
        cache_key = f"clients_{func.__name__}_{hash(str(args) + str(kwargs))}"
        
        # Essayer de récupérer depuis le cache
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            print(f"👥 Données clients récupérées depuis le cache: {func.__name__}")
            return cached_result
        
        # Calculer et mettre en cache
        result = func(*args, **kwargs)
        cache_manager.set(cache_key, result, ttl=120)  # 2 minutes pour les données clients
        print(f"👥 Données clients calculées et mises en cache: {func.__name__}")
        
        return result
    
    return wrapper

def invalidate_client_cache():
    """Invalider le cache des clients après une modification"""
    keys_to_delete = []
    for key in cache_manager._cache.keys():
        if key.startswith('clients_') or key.startswith('stats_'):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_manager.delete(key)
    
    print(f"🗑️ Cache invalidé: {len(keys_to_delete)} entrées supprimées")

def get_cache_info():
    """Obtenir les informations du cache pour le debugging"""
    stats = cache_manager.get_stats()
    expired_count = cache_manager.cleanup_expired()
    
    return {
        **stats,
        'cleaned_expired': expired_count,
        'timestamp': datetime.now().isoformat()
    }