#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database handler for user management
Supports both MongoDB (cloud) and local JSON (fallback)
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from config import Config

logger = logging.getLogger(__name__)


class Database:
    """Database handler with MongoDB and JSON fallback"""
    
    def __init__(self):
        self.use_mongodb = False
        self.db = None
        self.collection = None
        self.json_file = "users_db.json"
        self.users_data = {}
        
        # Try MongoDB first
        if Config.MONGODB_URI:
            try:
                from pymongo import MongoClient
                
                client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
                client.server_info()  # Test connection
                
                self.db = client[Config.DATABASE_NAME]
                self.collection = self.db['users']
                self.use_mongodb = True
                
                logger.info("✅ Connected to MongoDB")
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {str(e)}")
                logger.info("Falling back to JSON database")
        
        # Fallback to JSON
        if not self.use_mongodb:
            self._load_json_db()
    
    def _load_json_db(self):
        """Load users from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    self.users_data = json.load(f)
                logger.info(f"Loaded {len(self.users_data)} users from JSON")
            else:
                self.users_data = {}
        except Exception as e:
            logger.error(f"Error loading JSON database: {str(e)}")
            self.users_data = {}
    
    def _save_json_db(self):
        """Save users to JSON file"""
        try:
            with open(self.json_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving JSON database: {str(e)}")
    
    def add_user(self, user_id: int, username: str = None) -> bool:
        """Add or update user"""
        try:
            user_id_str = str(user_id)
            
            if self.use_mongodb:
                # MongoDB
                self.collection.update_one(
                    {'user_id': user_id},
                    {
                        '$set': {
                            'user_id': user_id,
                            'username': username,
                            'last_seen': datetime.now(),
                        },
                        '$setOnInsert': {
                            'joined_date': datetime.now(),
                            'total_downloads': 0,
                        }
                    },
                    upsert=True
                )
            else:
                # JSON
                if user_id_str not in self.users_data:
                    self.users_data[user_id_str] = {
                        'user_id': user_id,
                        'username': username,
                        'joined_date': datetime.now().isoformat(),
                        'total_downloads': 0,
                    }
                
                self.users_data[user_id_str]['last_seen'] = datetime.now().isoformat()
                self.users_data[user_id_str]['username'] = username
                
                self._save_json_db()
            
            return True
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return False
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user data"""
        try:
            user_id_str = str(user_id)
            
            if self.use_mongodb:
                return self.collection.find_one({'user_id': user_id})
            else:
                return self.users_data.get(user_id_str)
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs"""
        try:
            if self.use_mongodb:
                users = self.collection.find({}, {'user_id': 1})
                return [user['user_id'] for user in users]
            else:
                return [int(uid) for uid in self.users_data.keys()]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    def get_total_users(self) -> int:
        """Get total user count"""
        try:
            if self.use_mongodb:
                return self.collection.count_documents({})
            else:
                return len(self.users_data)
        except Exception as e:
            logger.error(f"Error getting total users: {str(e)}")
            return 0
    
    def increment_downloads(self, user_id: int) -> bool:
        """Increment user download count"""
        try:
            user_id_str = str(user_id)
            
            if self.use_mongodb:
                self.collection.update_one(
                    {'user_id': user_id},
                    {'$inc': {'total_downloads': 1}}
                )
            else:
                if user_id_str in self.users_data:
                    self.users_data[user_id_str]['total_downloads'] = \
                        self.users_data[user_id_str].get('total_downloads', 0) + 1
                    self._save_json_db()
            
            return True
        except Exception as e:
            logger.error(f"Error incrementing downloads: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            user_id_str = str(user_id)
            
            if self.use_mongodb:
                self.collection.delete_one({'user_id': user_id})
            else:
                if user_id_str in self.users_data:
                    del self.users_data[user_id_str]
                    self._save_json_db()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        try:
            user = self.get_user(user_id)
            
            if user:
                return {
                    'total_downloads': user.get('total_downloads', 0),
                    'joined_date': user.get('joined_date'),
                    'last_seen': user.get('last_seen'),
                }
            
            return {'total_downloads': 0}
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {'total_downloads': 0}
