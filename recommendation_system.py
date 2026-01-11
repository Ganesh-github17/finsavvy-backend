import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pandas as pd
from datetime import datetime

class RecommendationSystem:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.user_interactions = {}
        self.courses_db = {}
        
    def update_user_interaction(self, user_id: str, interaction_data: Dict):
        """
        Update user interaction data for better recommendations
        """
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = []
        self.user_interactions[user_id].append({
            **interaction_data,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_course_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[Dict]:
        """
        Get personalized course recommendations based on user interaction history
        """
        if user_id not in self.user_interactions:
            return self._get_trending_courses(n_recommendations)
            
        user_history = self.user_interactions[user_id]
        
        # Extract user preferences and create feature vector
        user_interests = " ".join([
            interaction.get("category", "") + " " +
            interaction.get("tags", "") + " " +
            interaction.get("difficulty", "")
            for interaction in user_history
        ])
        
        # Calculate similarity with available courses
        course_vectors = self.vectorizer.fit_transform([user_interests] + 
                                                     [course["description"] for course in self.courses_db.values()])
        similarities = cosine_similarity(course_vectors[0:1], course_vectors[1:])
        
        # Get top N recommendations
        top_indices = similarities[0].argsort()[-n_recommendations:][::-1]
        recommendations = [list(self.courses_db.values())[i] for i in top_indices]
        
        return recommendations
        
    def _get_trending_courses(self, n_courses: int = 5) -> List[Dict]:
        """
        Get trending courses for new users
        """
        # In a real implementation, this would be based on overall popularity
        return list(self.courses_db.values())[:n_courses]
