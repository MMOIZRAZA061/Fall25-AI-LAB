from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Global variables
model = None
label_encoders = {}
df_original = None

def load_resources():
    """Load model, data and create encoders"""
    global model, label_encoders, df_original
    
    try:
        # Load trained model
        with open('random_forest_model.pkl', 'rb') as file:
            model = pickle.load(file)
        print("✅ Model loaded successfully!")
        
        # Load original data
        df_original = pd.read_csv("recomdata.csv")
        print("✅ Dataset loaded successfully!")
        
        # Create label encoders
        categorical_columns = ['interests', 'category', 'preferred_difficulty', 
                             'past_experience', 'preferred_language', 'recommended_course']
        
        for col in categorical_columns:
            if col in df_original.columns:
                le = LabelEncoder()
                le.fit(df_original[col])
                label_encoders[col] = le
        
        print("✅ Label encoders created successfully!")
        
    except Exception as e:
        print(f"❌ Error loading resources: {e}")

def preprocess_input(user_data):
    """Preprocess user input for prediction"""
    
    features = []
    feature_columns = ['interests', 'category', 'preferred_difficulty', 
                      'past_experience', 'preferred_language']
    
    for feature in feature_columns:
        if feature in label_encoders:
            le = label_encoders[feature]
            try:
                encoded_value = le.transform([user_data[feature]])[0]
                features.append(encoded_value)
            except ValueError:
                # If new value, use the most common class
                features.append(0)
                print(f"⚠️  {user_data[feature]} not found in {feature} classes")
        else:
            features.append(0)
    
    return np.array([features])

def get_unique_values():
    """Get unique values for dropdowns"""
    if df_original is not None:
        return {
            'interests': sorted(df_original['interests'].unique()),
            'categories': sorted(df_original['category'].unique()),
            'difficulties': sorted(df_original['preferred_difficulty'].unique()),
            'experiences': sorted(df_original['past_experience'].unique()),
            'languages': sorted(df_original['preferred_language'].unique())
        }
    return {}

# Load resources when app starts
load_resources()

@app.route('/')
def home():
    unique_values = get_unique_values()
    return render_template('index.html', **unique_values)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_data = {
            'interests': request.form['interests'],
            'category': request.form['category'],
            'preferred_difficulty': request.form['preferred_difficulty'],
            'past_experience': request.form['past_experience'],
            'preferred_language': request.form['preferred_language']
        }
        
        # Store in session for result page
        session['user_input'] = user_data
        
        # Preprocess and predict
        processed_input = preprocess_input(user_data)
        prediction_encoded = model.predict(processed_input)[0]
        
        # Decode prediction
        if 'recommended_course' in label_encoders:
            recommended_course = label_encoders['recommended_course'].inverse_transform([prediction_encoded])[0]
        else:
            recommended_course = f"Course_{prediction_encoded}"
        
        # Get confidence score
        try:
            probabilities = model.predict_proba(processed_input)[0]
            confidence = round(max(probabilities) * 100, 2)
        except:
            confidence = "N/A"
        
        # Store in session
        session['recommendation'] = recommended_course
        session['confidence'] = confidence
        
        return render_template('result.html', 
                             recommendation=recommended_course,
                             confidence=confidence,
                             user_input=user_data)
    
    except Exception as e:
        unique_values = get_unique_values()
        return render_template('index.html', 
                             error=f"Prediction error: {str(e)}",
                             **unique_values)

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """API endpoint for JSON responses"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_data = {
            'interests': data.get('interests', ''),
            'category': data.get('category', ''),
            'preferred_difficulty': data.get('preferred_difficulty', ''),
            'past_experience': data.get('past_experience', ''),
            'preferred_language': data.get('preferred_language', '')
        }
        
        # Validate required fields
        for key, value in user_data.items():
            if not value:
                return jsonify({'error': f'{key} is required'}), 400
        
        # Preprocess and predict
        processed_input = preprocess_input(user_data)
        prediction_encoded = model.predict(processed_input)[0]
        
        # Decode prediction
        if 'recommended_course' in label_encoders:
            recommended_course = label_encoders['recommended_course'].inverse_transform([prediction_encoded])[0]
        else:
            recommended_course = f"Course_{prediction_encoded}"
        
        # Get confidence
        try:
            probabilities = model.predict_proba(processed_input)[0]
            confidence = round(max(probabilities) * 100, 2)
        except:
            confidence = "N/A"
        
        return jsonify({
            'success': True,
            'recommended_course': recommended_course,
            'confidence': confidence,
            'user_input': user_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories')
def api_categories():
    """API endpoint to get all available categories"""
    unique_values = get_unique_values()
    return jsonify(unique_values)

@app.route('/about')
def about():
    return render_template('index.html', show_about=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)