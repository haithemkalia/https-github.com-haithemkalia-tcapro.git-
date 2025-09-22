#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de base de données pour le système de suivi des visas TCA
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = None):
        """Initialiser le gestionnaire de base de données"""
        # Pour Vercel/Render : utiliser SQLite en mémoire ou un chemin temporaire
        import os
        import tempfile
        if os.environ.get('VERCEL') or os.environ.get('RENDER'):
            # En production Vercel/Render : utiliser un fichier temporaire
            temp_dir = tempfile.gettempdir()
            self.db_path = os.path.join(temp_dir, 'visa_system_render.db')
        else:
            # En local : utiliser le fichier local
            self.db_path = db_path or 'visa_system.db'
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données et créer les tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Créer la table clients si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT UNIQUE,
                full_name TEXT,
                whatsapp_number TEXT,
                whatsapp_number_clean TEXT,
                application_date TEXT,
                transaction_date TEXT,
                passport_number TEXT UNIQUE,
                passport_status TEXT,
                passport_status_normalized TEXT,
                nationality TEXT,
                visa_status TEXT,
                visa_status_normalized TEXT,
                processed_by TEXT,
                summary TEXT,
                notes TEXT,
                responsible_employee TEXT,
                original_row_number INTEGER,
                import_timestamp TEXT,
                is_duplicate BOOLEAN DEFAULT FALSE,
                auto_generated_id BOOLEAN DEFAULT FALSE,
                empty_name_accepted BOOLEAN DEFAULT FALSE,
                extra_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Si on est sur Vercel/Render et que la base est vide, ajouter des données de test
        import os
        if os.environ.get('VERCEL') or os.environ.get('RENDER'):
            cursor.execute('SELECT COUNT(*) FROM clients')
            count = cursor.fetchone()[0]
            if count == 0:
                # Ajouter quelques clients de test
                test_clients = [
                    {
                        'client_id': 'TEST001',
                        'full_name': 'Client Test 1',
                        'whatsapp_number': '+21612345678',
                        'nationality': 'Tunisienne',
                        'visa_status': 'En cours',
                        'responsible_employee': 'Employé Test'
                    },
                    {
                        'client_id': 'TEST002', 
                        'full_name': 'Client Test 2',
                        'whatsapp_number': '+21687654321',
                        'nationality': 'Marocaine',
                        'visa_status': 'Validé',
                        'responsible_employee': 'Employé Test'
                    }
                ]
                
                for client in test_clients:
                    cursor.execute('''
                        INSERT INTO clients (client_id, full_name, whatsapp_number, nationality, visa_status, responsible_employee)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (client['client_id'], client['full_name'], client['whatsapp_number'], 
                          client['nationality'], client['visa_status'], client['responsible_employee']))
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def add_client(self, client_data: Dict[str, Any]) -> Optional[int]:
        """Ajouter un nouveau client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO clients (
                    client_id, full_name, whatsapp_number, whatsapp_number_clean,
                    application_date, transaction_date, passport_number, passport_status,
                    passport_status_normalized, nationality, visa_status, visa_status_normalized,
                    processed_by, summary, notes, responsible_employee, original_row_number,
                    import_timestamp, is_duplicate, auto_generated_id, empty_name_accepted,
                    extra_data, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_data.get('client_id'),
                client_data.get('full_name'),
                client_data.get('whatsapp_number'),
                client_data.get('whatsapp_number_clean'),
                client_data.get('application_date'),
                client_data.get('transaction_date'),
                client_data.get('passport_number'),
                client_data.get('passport_status'),
                client_data.get('passport_status_normalized'),
                client_data.get('nationality'),
                client_data.get('visa_status'),
                client_data.get('visa_status_normalized'),
                client_data.get('processed_by'),
                client_data.get('summary'),
                client_data.get('notes'),
                client_data.get('responsible_employee'),
                client_data.get('original_row_number'),
                client_data.get('import_timestamp'),
                client_data.get('is_duplicate', False),
                client_data.get('auto_generated_id', False),
                client_data.get('empty_name_accepted', False),
                client_data.get('extra_data'),
                client_data.get('created_at', datetime.now().isoformat())
            ))
            
            client_id = cursor.lastrowid
            conn.commit()
            return client_data.get('client_id')
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_all_clients(self) -> int:
        """Supprimer tous les clients - retourne le nombre de clients supprimés"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Compter les clients avant suppression
            cursor.execute('SELECT COUNT(*) FROM clients')
            count_before = cursor.fetchone()[0]
            
            # Supprimer tous les clients
            cursor.execute('DELETE FROM clients')
            
            # Valider la transaction
            conn.commit()
            
            return count_before
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_clients(self, page: int = 1, per_page: int = 50) -> tuple[List[sqlite3.Row], int]:
        """Récupérer tous les clients avec pagination"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Compter le total
            cursor.execute('SELECT COUNT(*) FROM clients')
            total = cursor.fetchone()[0]
            
            # Calculer l'offset
            offset = (page - 1) * per_page
            
            # Récupérer les clients paginés avec tri décroissant par client_id (plus récent en premier)
            cursor.execute("""
                SELECT * FROM clients 
                ORDER BY 
                    CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC,
                    client_id DESC 
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            clients = cursor.fetchall()
            return clients, total
        finally:
            conn.close()
    
    def get_client_by_id(self, client_id: str) -> Optional[sqlite3.Row]:
        """Récupérer un client par son ID"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
            client = cursor.fetchone()
            return client
        finally:
            conn.close()
    
    def is_passport_number_unique(self, passport_number: str, exclude_client_id: str = None) -> bool:
        """Vérifier si le numéro de passeport est unique"""
        if not passport_number or not passport_number.strip():
            return True  # Les numéros vides sont autorisés
        
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if exclude_client_id:
                cursor.execute(
                    'SELECT COUNT(*) as count FROM clients WHERE passport_number = ? AND client_id != ?', 
                    (passport_number.strip(), exclude_client_id)
                )
            else:
                cursor.execute(
                    'SELECT COUNT(*) as count FROM clients WHERE passport_number = ?', 
                    (passport_number.strip(),)
                )
            
            result = cursor.fetchone()
            return result['count'] == 0
        finally:
            conn.close()
    
    def search_clients(self, search_term: str, page: int = 1, per_page: int = 50) -> tuple[List[sqlite3.Row], int]:
        """Rechercher des clients avec pagination"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            search_pattern = f'%{search_term}%'
            
            # Compter le total des résultats
            cursor.execute('''
                SELECT COUNT(*) FROM clients 
                WHERE full_name LIKE ? 
                   OR client_id LIKE ? 
                   OR whatsapp_number LIKE ? 
                   OR passport_number LIKE ?
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            total = cursor.fetchone()[0]
            
            # Calculer l'offset
            offset = (page - 1) * per_page
            
            # Récupérer les clients paginés avec tri chronologique par client_id
            cursor.execute('''
                SELECT * FROM clients 
                WHERE full_name LIKE ? 
                   OR client_id LIKE ? 
                   OR whatsapp_number LIKE ? 
                   OR passport_number LIKE ?
                ORDER BY 
                   CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC,
                   client_id ASC
                LIMIT ? OFFSET ?
            ''', (search_pattern, search_pattern, search_pattern, search_pattern, per_page, offset))
            
            clients = cursor.fetchall()
            return clients, total
        finally:
            conn.close()
    
    def get_filtered_clients(self, filters: Dict[str, str] = None, page: int = 1, per_page: int = 50) -> tuple[List[sqlite3.Row], int]:
        """Récupérer les clients avec filtres et pagination"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Construire la requête WHERE dynamiquement
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('search'):
                    search_pattern = f"%{filters['search']}%"
                    where_conditions.append(
                        "(full_name LIKE ? OR client_id LIKE ? OR whatsapp_number LIKE ? OR passport_number LIKE ?)"
                    )
                    params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
                
                if filters.get('visa_status'):
                    where_conditions.append("visa_status = ?")
                    params.append(filters['visa_status'])
                
                if filters.get('nationality'):
                    where_conditions.append("nationality = ?")
                    params.append(filters['nationality'])
                
                if filters.get('responsible_employee'):
                    where_conditions.append("responsible_employee = ?")
                    params.append(filters['responsible_employee'])
            
            # Construire la clause WHERE
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Compter le total
            count_query = f"SELECT COUNT(*) FROM clients {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Calculer l'offset
            offset = (page - 1) * per_page
            
            # Récupérer les clients paginés avec tri chronologique par client_id
            select_query = (
                f"SELECT * FROM clients {where_clause} "
                "ORDER BY "
                "CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC, "
                "client_id ASC "
                "LIMIT ? OFFSET ?"
            )
            cursor.execute(select_query, params + [per_page, offset])
            clients = cursor.fetchall()
            
            return clients, total
        finally:
            conn.close()
    
    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """Mettre à jour un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ajouter la date de mise à jour automatiquement
            current_timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE clients SET
                    full_name = ?, whatsapp_number = ?, whatsapp_number_clean = ?,
                    application_date = ?, transaction_date = ?, passport_number = ?,
                    passport_status = ?, passport_status_normalized = ?, nationality = ?,
                    visa_status = ?, visa_status_normalized = ?, processed_by = ?,
                    summary = ?, notes = ?, responsible_employee = ?, updated_at = ?
                WHERE client_id = ?
            ''', (
                client_data.get('full_name'),
                client_data.get('whatsapp_number'),
                client_data.get('whatsapp_number_clean'),
                client_data.get('application_date'),
                client_data.get('transaction_date'),
                client_data.get('passport_number'),
                client_data.get('passport_status'),
                client_data.get('passport_status_normalized'),
                client_data.get('nationality'),
                client_data.get('visa_status'),
                client_data.get('visa_status_normalized'),
                client_data.get('processed_by'),
                client_data.get('summary'),
                client_data.get('notes'),
                client_data.get('responsible_employee'),
                current_timestamp,
                client_id
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_client_field(self, client_id: str, field: str, value: str) -> bool:
        """Mettre à jour un champ spécifique d'un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier que le client existe
            cursor.execute('SELECT id FROM clients WHERE client_id = ?', (client_id,))
            if not cursor.fetchone():
                return False
            
            # Mettre à jour le champ spécifique
            current_timestamp = datetime.now().isoformat()
            
            if field == 'visa_status':
                cursor.execute('''
                    UPDATE clients SET visa_status = ?, visa_status_normalized = ?, updated_at = ?
                    WHERE client_id = ?
                ''', (value, value.lower().replace(' ', '_'), current_timestamp, client_id))
            elif field == 'responsible_employee':
                cursor.execute('''
                    UPDATE clients SET responsible_employee = ?, updated_at = ?
                    WHERE client_id = ?
                ''', (value, current_timestamp, client_id))
            elif field == 'application_date':
                cursor.execute('''
                    UPDATE clients SET application_date = ?, updated_at = ?
                    WHERE client_id = ?
                ''', (value, current_timestamp, client_id))
            elif field == 'transaction_date':
                cursor.execute('''
                    UPDATE clients SET transaction_date = ?, updated_at = ?
                    WHERE client_id = ?
                ''', (value, current_timestamp, client_id))
            else:
                return False
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la mise à jour du champ {field}: {e}")
            return False
        finally:
            conn.close()
    
    def update_client_by_db_id(self, db_id: int, client_data: Dict[str, Any]) -> bool:
        """Mettre à jour un client par son ID de base de données (clé primaire)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ajouter la date de mise à jour automatiquement
            current_timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE clients SET
                    client_id = ?, full_name = ?, whatsapp_number = ?, whatsapp_number_clean = ?,
                    application_date = ?, transaction_date = ?, passport_number = ?,
                    passport_status = ?, passport_status_normalized = ?, nationality = ?,
                    visa_status = ?, visa_status_normalized = ?, processed_by = ?,
                    summary = ?, notes = ?, responsible_employee = ?, updated_at = ?
                WHERE id = ?
            ''', (
                client_data.get('client_id'),
                client_data.get('full_name'),
                client_data.get('whatsapp_number'),
                client_data.get('whatsapp_number_clean'),
                client_data.get('application_date'),
                client_data.get('transaction_date'),
                client_data.get('passport_number'),
                client_data.get('passport_status'),
                client_data.get('passport_status_normalized'),
                client_data.get('nationality'),
                client_data.get('visa_status'),
                client_data.get('visa_status_normalized'),
                client_data.get('processed_by'),
                client_data.get('summary'),
                client_data.get('notes'),
                client_data.get('responsible_employee'),
                current_timestamp,
                db_id
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_client(self, client_id: str) -> bool:
        """Supprimer un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM clients WHERE client_id = ?', (client_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupérer les statistiques"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Compter le total
            cursor.execute('SELECT COUNT(*) FROM clients')
            total = cursor.fetchone()[0]
            
            # Statistiques par statut
            cursor.execute('''
                SELECT visa_status, COUNT(*) 
                FROM clients 
                GROUP BY visa_status
            ''')
            by_status = dict(cursor.fetchall())
            
            # Statistiques par nationalité
            cursor.execute('''
                SELECT nationality, COUNT(*) 
                FROM clients 
                GROUP BY nationality
            ''')
            by_nationality = dict(cursor.fetchall())
            
            # Statistiques par employé
            cursor.execute('''
                SELECT responsible_employee, COUNT(*) 
                FROM clients 
                GROUP BY responsible_employee
            ''')
            by_employee = dict(cursor.fetchall())
            
            return {
                'total': total,
                'by_status': by_status,
                'by_nationality': by_nationality,
                'by_employee': by_employee
            }
            
        finally:
            conn.close()