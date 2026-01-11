import os
import fitz  # PyMuPDF for PDF handling
import json
from datetime import datetime
from typing import Dict, List
import logging
from flask import jsonify
import uuid

logger = logging.getLogger(__name__)

class CollaborationManager:
    def __init__(self):
        self.upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        self.notes_dir = os.path.join(self.upload_dir, "notes")
        self.resources_dir = os.path.join(self.upload_dir, "resources")
        
        # Create directories if they don't exist
        for directory in [self.upload_dir, self.notes_dir, self.resources_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # Initialize data stores
        self.notes_db_path = os.path.join(self.upload_dir, "notes.json")
        self.resources_db_path = os.path.join(self.upload_dir, "resources.json")
        self.study_groups_db_path = os.path.join(self.upload_dir, "study_groups.json")
        
        self._load_data()
        
    def _load_data(self):
        """Load data from JSON files"""
        self.notes = self._load_json(self.notes_db_path, [])
        self.resources = self._load_json(self.resources_db_path, [])
        self.study_groups = self._load_json(self.study_groups_db_path, {})
        
    def _load_json(self, path: str, default: any) -> any:
        """Load JSON file or return default if file doesn't exist"""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {str(e)}")
        return default
        
    def _save_json(self, path: str, data: any):
        """Save data to JSON file"""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving to {path}: {str(e)}")

    def save_note(self, title: str, content: str, user_id: str, course_id: str = None) -> Dict:
        """Save a new note"""
        try:
            note = {
                "id": len(self.notes) + 1,
                "title": title,
                "content": content,
                "user_id": user_id,
                "course_id": course_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.notes.append(note)
            self._save_json(self.notes_db_path, self.notes)
            
            return {
                "success": True,
                "note": note
            }
            
        except Exception as e:
            logger.error(f"Error saving note: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_notes(self, user_id: str, course_id: str = None) -> List[Dict]:
        """Get notes for a user and optionally filtered by course"""
        try:
            user_notes = [n for n in self.notes if n["user_id"] == user_id]
            if course_id:
                user_notes = [n for n in user_notes if n["course_id"] == course_id]
            return user_notes
        except Exception as e:
            logger.error(f"Error getting notes: {str(e)}")
            return []

    def save_pdf(self, content: bytes, filename: str, user_id: str) -> Dict:
        """Save an uploaded PDF file"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{user_id}_{timestamp}_{filename}"
            file_path = os.path.join(self.resources_dir, safe_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(content)
                
            # Extract text for searching
            doc = fitz.open(file_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            
            # Save resource metadata
            resource = {
                "id": len(self.resources) + 1,
                "filename": safe_filename,
                "original_filename": filename,
                "user_id": user_id,
                "file_path": file_path,
                "text_content": text_content,
                "uploaded_at": datetime.now().isoformat()
            }
            
            self.resources.append(resource)
            self._save_json(self.resources_db_path, self.resources)
            
            return {
                "success": True,
                "resource": {
                    "id": resource["id"],
                    "filename": resource["original_filename"],
                    "uploaded_at": resource["uploaded_at"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_pdfs(self, query: str) -> List[Dict]:
        """Search through uploaded PDFs"""
        try:
            results = []
            query = query.lower()
            
            for resource in self.resources:
                text_content = resource["text_content"].lower()
                if query in text_content:
                    # Find the context around the match
                    start_idx = text_content.find(query)
                    context_start = max(0, start_idx - 100)
                    context_end = min(len(text_content), start_idx + len(query) + 100)
                    context = text_content[context_start:context_end]
                    
                    results.append({
                        "id": resource["id"],
                        "filename": resource["original_filename"],
                        "context": f"...{context}...",
                        "uploaded_at": resource["uploaded_at"]
                    })
                    
            return results
            
        except Exception as e:
            logger.error(f"Error searching PDFs: {str(e)}")
            return []

    def create_study_group(self, name: str, description: str, course_id: str, created_by: str) -> Dict:
        """Create a new study group"""
        try:
            group_id = str(len(self.study_groups) + 1)
            group = {
                "id": group_id,
                "name": name,
                "description": description,
                "course_id": course_id,
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "members": [created_by],
                "messages": [],
                "resources": []
            }
            
            self.study_groups[group_id] = group
            self._save_json(self.study_groups_db_path, self.study_groups)
            
            return {
                "success": True,
                "group": group
            }
            
        except Exception as e:
            logger.error(f"Error creating study group: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def join_study_group(self, group_id: str, user_id: str) -> Dict:
        """Join a study group"""
        try:
            if group_id not in self.study_groups:
                return {
                    "success": False,
                    "error": "Study group not found"
                }
                
            if user_id not in self.study_groups[group_id]["members"]:
                self.study_groups[group_id]["members"].append(user_id)
                self._save_json(self.study_groups_db_path, self.study_groups)
                
            return {
                "success": True,
                "group": self.study_groups[group_id]
            }
            
        except Exception as e:
            logger.error(f"Error joining study group: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_study_groups(self, user_id: str = None, course_id: str = None) -> List[Dict]:
        """Get study groups, optionally filtered by user or course"""
        try:
            groups = list(self.study_groups.values())
            
            if user_id:
                groups = [g for g in groups if user_id in g["members"]]
                
            if course_id:
                groups = [g for g in groups if g["course_id"] == course_id]
                
            return groups
            
        except Exception as e:
            logger.error(f"Error getting study groups: {str(e)}")
            return []

    def get_student_groups(self):
        """Get all student groups"""
        return {'groups': list(self.study_groups.values())}

    def get_group_by_id(self, group_id):
        """Get a specific student group by ID"""
        if group_id in self.study_groups:
            return self.study_groups[group_id]
        return None

    def create_group(self, data):
        """Create a new student group"""
        group_id = str(uuid.uuid4())
        new_group = {
            'id': group_id,
            'name': data['name'],
            'description': data['description'],
            'members': [{'id': data['creator_id'], 'name': data['creator_name'], 'role': 'admin'}],
            'discussions': []
        }
        self.study_groups[group_id] = new_group
        self._save_json(self.study_groups_db_path, self.study_groups)
        return new_group

    def add_group_discussion(self, group_id, data):
        """Add a discussion to a student group"""
        if group_id in self.study_groups:
            discussion = {
                'id': str(uuid.uuid4()),
                'title': data['title'],
                'content': data['content'],
                'created_at': datetime.now().isoformat(),
                'author': data['author']
            }
            self.study_groups[group_id]['discussions'].append(discussion)
            self._save_json(self.study_groups_db_path, self.study_groups)
            return discussion
        return None

    def get_resources(self):
        """Get all uploaded resources"""
        return {'resources': self.resources}

    def add_resource(self, data):
        """Add a new resource"""
        resource_id = str(uuid.uuid4())
        new_resource = {
            'id': resource_id,
            'name': data['name'],
            'type': data['type'],
            'size': data['size'],
            'uploaded_by': data['uploaded_by'],
            'uploaded_at': datetime.now().isoformat(),
            'description': data['description'],
            'tags': data['tags']
        }
        self.resources.append(new_resource)
        self._save_json(self.resources_db_path, self.resources)
        return new_resource

# Initialize collaboration manager
collaboration_manager = CollaborationManager()
