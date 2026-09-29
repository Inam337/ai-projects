import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class QueryManager:
    """Manage saved search queries"""
    
    def __init__(self, storage_file: str = "saved_queries.json"):
        self.storage_file = storage_file
        self.queries: List[Dict] = []
        self.load_queries()
    
    def load_queries(self):
        """Load saved queries from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.queries = json.load(f)
            except:
                self.queries = []
        else:
            self.queries = []
    
    def save_queries(self):
        """Save queries to file"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.queries, f, indent=2, ensure_ascii=False)
    
    def save_query(self, query: str, name: str = None, query_type: str = "people_search") -> str:
        """Save a query with optional name"""
        if not name:
            name = f"Query {len(self.queries) + 1}"
        
        query_data = {
            "id": f"Q{len(self.queries) + 1:04d}",
            "name": name,
            "query": query,
            "type": query_type,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        self.queries.append(query_data)
        self.save_queries()
        return query_data["id"]
    
    def rename_query(self, query_id: str, new_name: str) -> bool:
        """Rename a saved query"""
        for query in self.queries:
            if query["id"] == query_id:
                query["name"] = new_name
                query["updated_at"] = datetime.now().isoformat()
                self.save_queries()
                return True
        return False
    
    def delete_query(self, query_id: str) -> bool:
        """Delete a saved query"""
        initial_count = len(self.queries)
        self.queries = [q for q in self.queries if q["id"] != query_id]
        if len(self.queries) < initial_count:
            self.save_queries()
            return True
        return False
    
    def get_query(self, query_id: str) -> Optional[Dict]:
        """Get a query by ID"""
        for query in self.queries:
            if query["id"] == query_id:
                query["last_used"] = datetime.now().isoformat()
                self.save_queries()
                return query
        return None
    
    def list_queries(self, query_type: str = None) -> List[Dict]:
        """List all queries, optionally filtered by type"""
        if query_type:
            return [q for q in self.queries if q.get("type") == query_type]
        return self.queries.copy()






