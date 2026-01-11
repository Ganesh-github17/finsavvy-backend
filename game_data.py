from typing import Dict, List
import uuid
from datetime import datetime

# Store game scores in memory (in a real app, this would be in a database)
game_scores: Dict[str, List[Dict]] = {}

def save_game_score(user_id: str, score: int, completion_time: float):
    """Save a game score for a user"""
    if user_id not in game_scores:
        game_scores[user_id] = []
    
    game_scores[user_id].append({
        'id': str(uuid.uuid4()),
        'score': score,
        'completion_time': completion_time,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only top 10 scores
    game_scores[user_id] = sorted(
        game_scores[user_id],
        key=lambda x: (x['score'], -x['completion_time']),
        reverse=True
    )[:10]

def get_user_scores(user_id: str) -> List[Dict]:
    """Get all scores for a user"""
    return game_scores.get(user_id, [])

def get_leaderboard() -> List[Dict]:
    """Get global leaderboard"""
    all_scores = []
    for user_id, scores in game_scores.items():
        if scores:
            best_score = max(scores, key=lambda x: (x['score'], -x['completion_time']))
            all_scores.append({
                'user_id': user_id,
                'score': best_score['score'],
                'completion_time': best_score['completion_time'],
                'timestamp': best_score['timestamp']
            })
    
    return sorted(all_scores, key=lambda x: (x['score'], -x['completion_time']), reverse=True)[:10]
