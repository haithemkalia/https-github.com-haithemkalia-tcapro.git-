#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de cache simple pour améliorer les performances
"""

import time
import json
import os
from typing import Any, Optional

class SimpleCache:
    """Cache simple en mémoire"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes par défaut
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Stocker une valeur dans le cache"""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Vider le cache"""
        self.cache.clear()
    
    def invalidate(self, pattern: str) -> None:
        """Invalider les clés correspondant au pattern"""
        keys_to_remove = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]

# Instance globale du cache
cache = SimpleCache(ttl=300)  # 5 minutes

def get_cached_clients(page: int, per_page: int):
    """Récupérer les clients depuis le cache"""
    cache_key = f"clients_{page}_{per_page}"
    return cache.get(cache_key)

def set_cached_clients(page: int, per_page: int, data):
    """Stocker les clients dans le cache"""
    cache_key = f"clients_{page}_{per_page}"
    cache.set(cache_key, data)

def invalidate_client_cache():
    """Invalider le cache des clients"""
    cache.invalidate("clients_")
