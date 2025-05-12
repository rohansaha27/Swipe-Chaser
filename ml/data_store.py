"""
Data Store for Swipe Chaser
Manages persistent storage of player data and model parameters
"""
import os
import json
import time
import joblib

class PlayerDataStore:
    def __init__(self, data_dir='./data'):
        """
        Initialize the data store
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.player_data_file = os.path.join(data_dir, 'player_data.json')
        self.model_file = os.path.join(data_dir, 'difficulty_model.joblib')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Load player data if it exists
        self.player_data = self._load_player_data()
    
    def _load_player_data(self):
        """Load player data from disk"""
        if os.path.exists(self.player_data_file):
            try:
                with open(self.player_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading player data: {e}")
        
        # Return default data if file doesn't exist or there's an error
        return {
            'total_play_time': 0,
            'high_score': 0,
            'games_played': 0,
            'last_session': None,
            'difficulty_history': [],
            'performance_history': []
        }
    
    def save_player_data(self):
        """Save player data to disk"""
        try:
            with open(self.player_data_file, 'w') as f:
                json.dump(self.player_data, f)
            return True
        except Exception as e:
            print(f"Error saving player data: {e}")
            return False
    
    def update_session_data(self, play_time, score):
        """
        Update player data after a game session
        
        Args:
            play_time: Time played in seconds
            score: Score achieved in the session
        """
        # Update player data
        self.player_data['total_play_time'] += play_time
        self.player_data['games_played'] += 1
        self.player_data['last_session'] = time.time()
        
        # Update high score if necessary
        if score > self.player_data.get('high_score', 0):
            self.player_data['high_score'] = score
        
        # Save updated data
        self.save_player_data()
    
    def add_difficulty_record(self, metrics, params, score, duration):
        """
        Add a record of difficulty parameters and performance
        
        Args:
            metrics: Player metrics at the end of the session
            params: Difficulty parameters used
            score: Final score
            duration: Session duration in seconds
        """
        # Create record
        record = {
            'timestamp': time.time(),
            'metrics': metrics,
            'params': params,
            'score': score,
            'duration': duration
        }
        
        # Add to history
        self.player_data['difficulty_history'].append(record)
        
        # Keep only the last 20 records to avoid file size growth
        if len(self.player_data['difficulty_history']) > 20:
            self.player_data['difficulty_history'] = self.player_data['difficulty_history'][-20:]
        
        # Save updated data
        self.save_player_data()
    
    def get_player_stats(self):
        """
        Get player statistics
        
        Returns:
            dict: Player statistics
        """
        return {
            'total_play_time': self.player_data['total_play_time'],
            'high_score': self.player_data['high_score'],
            'games_played': self.player_data['games_played'],
            'last_session': self.player_data['last_session']
        }
    
    def save_model(self, model, scaler):
        """
        Save model and scaler to disk
        
        Args:
            model: Trained model
            scaler: Feature scaler
        """
        try:
            model_data = {
                'model': model,
                'scaler': scaler
            }
            joblib.dump(model_data, self.model_file)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self):
        """
        Load model and scaler from disk
        
        Returns:
            tuple: (model, scaler) if successful, (None, None) otherwise
        """
        if os.path.exists(self.model_file):
            try:
                model_data = joblib.load(self.model_file)
                return model_data['model'], model_data['scaler']
            except Exception as e:
                print(f"Error loading model: {e}")
        
        return None, None
