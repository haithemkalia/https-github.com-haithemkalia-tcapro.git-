#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package des modèles de données pour le système de suivi des visas TCA
"""

from .client import Client, ClientValidator

__all__ = ['Client', 'ClientValidator']