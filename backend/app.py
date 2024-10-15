from flask import Flask, request, jsonify
from flask_cors import CORS
from fastai.vision.all import *
import os

app = Flask(__name__)
CORS(app)

# Define the is_recyclable function used in model training
def is_recyclable(file_path):
    recyclable = ['cardboard', 'glass', 'metal', 'paper', 'plastic']
    category = file_path.parent.name
    return 'recyclable' if category in recyclable else 'non_recyclable'

# Load the saved model
try:
    learn = load_learner('./export.pkl', cpu=True)
except RuntimeError as e:
    print(f"Error loading the model: {e}")
    learn = None

@app.route('/predict', methods=['POST'])
def predict():
    if learn is None:
        return jsonify({'error': 'Model not loaded properly'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    try:
        # Read the image file
        img_bytes = file.read()
        img = PILImage.create(img_bytes)
        
        # Make prediction
        pred_class, pred_idx, probs = learn.predict(img)
        
        confidence = float(probs[pred_idx])
        
        # Check if the predicted class is recyclable
        recyclable = ['cardboard', 'glass', 'metal', 'paper', 'plastic']
        category = str(pred_class)
        recycling_status = 'recyclable' if category in recyclable else 'non_recyclable'
        
        return jsonify({
            'prediction': category,
            'confidence': confidence,
            'recycling_status': recycling_status
        })
    except Exception as e:
        return jsonify({'error': f'Error processing the image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
