"""
Difficulty Model for Swipe Chaser
Uses machine learning to dynamically adjust game difficulty based on player performance
"""
import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class DifficultyModel:
    def __init__(self, model_path=None):
        """
        Initialize the difficulty adjustment model
        
        Args:
            model_path: Path to a saved model file (optional)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False
        self.training_data = {
            'features': [],
            'targets': []
        }
        
        # Default difficulty parameters
        self.default_params = {
            'speed': 5.0,
            'obstacle_frequency': 30,
            'pattern_complexity': 1.0,
            'coin_value': 1
        }
        
        # Load existing model if provided
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new machine learning model"""
        self.model = RandomForestRegressor(
            n_estimators=10,
            max_depth=3,
            random_state=42
        )
        self.trained = False
    
    def _load_model(self, model_path):
        """Load a saved model from disk"""
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.trained = True
        except Exception as e:
            print(f"Error loading model: {e}")
            self._initialize_model()
    
    def save_model(self, model_path):
        """Save the current model to disk"""
        if not self.trained:
            return False
            
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler
            }
            joblib.dump(model_data, model_path)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def add_training_example(self, player_metrics, difficulty_params, success_rating):
        """
        Add a training example to improve the model
        
        Args:
            player_metrics: Dictionary of player performance metrics
            difficulty_params: Dictionary of difficulty parameters used
            success_rating: How successful this difficulty was (0-1, higher is better)
        """
        # Extract features from player metrics
        features = self._extract_features(player_metrics)
        
        # Extract targets (difficulty parameters that worked well)
        # We adjust the parameters based on success rating
        targets = []
        for param in ['speed', 'obstacle_frequency', 'pattern_complexity']:
            # If success is high, keep parameters similar
            # If success is low, adjust parameters to be easier
            adjustment = 1.0 if success_rating > 0.7 else (0.8 if success_rating > 0.4 else 0.6)
            targets.append(difficulty_params.get(param, self.default_params[param]) * adjustment)
        
        # Add to training data
        self.training_data['features'].append(features)
        self.training_data['targets'].append(targets)
        
        # Retrain model if we have enough data
        if len(self.training_data['features']) >= 10 and len(self.training_data['features']) % 5 == 0:
            self._train_model()
    
    def _extract_features(self, player_metrics):
        """Extract and normalize features from player metrics"""
        features = [
            player_metrics.get('reaction_time', 0.5),
            player_metrics.get('near_miss_distance', 50),
            player_metrics.get('coin_collection_rate', 0.5),
            player_metrics.get('lane_changes_per_minute', 10),
            player_metrics.get('obstacles_avoided', 0) / max(1, player_metrics.get('play_time', 1) / 60)
        ]
        return features
    
    def _train_model(self):
        """Train the model using collected data"""
        if len(self.training_data['features']) < 5:
            return
            
        X = np.array(self.training_data['features'])
        y = np.array(self.training_data['targets'])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        try:
            self.model.fit(X_scaled, y)
            self.trained = True
        except Exception as e:
            print(f"Error training model: {e}")
    
    def get_difficulty_params(self, player_metrics):
        """
        Get optimal difficulty parameters based on player metrics
        
        Args:
            player_metrics: Dictionary of player performance metrics
            
        Returns:
            dict: Dictionary of difficulty parameters
        """
        # Use default parameters if not trained or insufficient data
        if not self.trained or len(self.training_data['features']) < 5:
            return self._get_heuristic_params(player_metrics)
        
        # Extract features
        features = self._extract_features(player_metrics)
        features_scaled = self.scaler.transform([features])
        
        # Predict parameters
        try:
            params = self.model.predict(features_scaled)[0]
            
            return {
                'speed': max(3.0, min(10.0, params[0])),
                'obstacle_frequency': max(15, min(60, int(params[1]))),
                'pattern_complexity': max(1.0, min(3.0, params[2])),
                'coin_value': self._calculate_coin_value(player_metrics)
            }
        except Exception as e:
            print(f"Error predicting parameters: {e}")
            return self._get_heuristic_params(player_metrics)
    
    def _get_heuristic_params(self, player_metrics):
        """
        Get difficulty parameters using heuristics when ML model isn't ready
        
        Args:
            player_metrics: Dictionary of player performance metrics
            
        Returns:
            dict: Dictionary of difficulty parameters
        """
        # Extract key metrics with defaults if not available
        reaction_time = player_metrics.get('reaction_time', 0.5)
        coin_rate = player_metrics.get('coin_collection_rate', 0.5)
        lane_changes = player_metrics.get('lane_changes_per_minute', 10)
        play_time = player_metrics.get('play_time', 0)
        
        # Calculate skill score (0-1)
        skill_score = (
            (0.5 / max(0.1, reaction_time)) * 0.4 +  # Lower reaction time is better
            coin_rate * 0.3 +                        # Higher coin collection rate is better
            min(1.0, lane_changes / 20) * 0.3        # More lane changes (up to a point) is better
        )
        
        # Adjust for play time - new players get easier difficulty
        experience_factor = min(1.0, play_time / 300)  # Caps at 5 minutes of play
        adjusted_skill = skill_score * (0.5 + 0.5 * experience_factor)
        
        # Calculate parameters based on skill
        speed = 3.0 + adjusted_skill * 7.0  # Range: 3.0 - 10.0
        obstacle_freq = 60 - adjusted_skill * 45  # Range: 15 - 60 (higher is less frequent)
        pattern_complexity = 1.0 + adjusted_skill * 2.0  # Range: 1.0 - 3.0
        
        return {
            'speed': speed,
            'obstacle_frequency': int(obstacle_freq),
            'pattern_complexity': pattern_complexity,
            'coin_value': self._calculate_coin_value(player_metrics)
        }
    
    def _calculate_coin_value(self, player_metrics):
        """Calculate coin value based on player skill - harder difficulty gives more points"""
        # FIXED: Always return exactly 1 to fix scoring issues
        # We can re-enable dynamic coin values once the basic scoring is working
        return 1
        
        # Original dynamic coin value calculation (disabled for now)
        # coin_rate = player_metrics.get('coin_collection_rate', 0.5)
        # 
        # # If player is good at collecting coins, make them worth less
        # # If player struggles with coins, make them worth more
        # if coin_rate > 0.8:
        #     return 1  # Very good at collecting coins
        # elif coin_rate > 0.6:
        #     return 2  # Good at collecting coins
        # elif coin_rate > 0.4:
        #     return 3  # Average at collecting coins
        # else:
        #     return 5  # Struggling with coins
