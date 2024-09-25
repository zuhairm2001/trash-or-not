from flask import Flask, request, jsonify
from flask_cors import CORS
from fastai.vision.all import *
import os

app = Flask(__name__)
CORS(app)

# Define the is_recyclable function
def is_recyclable(file_path):
    recyclable = ['cardboard', 'glass', 'metal', 'paper', 'plastic']
    category = file_path.parent.name
    return 'recyclable' if category in recyclable else 'non_recyclable'

# Load the saved model
learn = load_learner('./export.pkl', cpu=True)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file:
        # Read the image file
        img_bytes = file.read()
        img = PILImage.create(img_bytes)
        
        # Make prediction
        pred_class, pred_idx, probs = learn.predict(img)
        
        confidence = float(probs[pred_idx])
        
        return jsonify({
            'prediction': str(pred_class),
            'confidence': confidence
        })

if __name__ == '__main__':
    app.run(debug=True)
