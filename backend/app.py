from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import os
from torchvision import transforms, models
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load the model
device = torch.device("cpu")
model = models.resnet34(weights=None)
num_ftrs = model.fc.in_features

# Match the architecture used during training with 6 output classes
model.fc = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(num_ftrs, 6)  # 6 classes from TrashNet dataset
)

# Load state dict
state_dict = torch.load('best_model.pth', map_location=device, weights_only=True)
fixed_state_dict = {}
for key in state_dict:
    if key.startswith('resnet.'):
        # Remove the 'resnet.' prefix
        fixed_key = key[7:]
        fixed_state_dict[fixed_key] = state_dict[key]
    else:
        fixed_state_dict[key] = state_dict[key]

model.load_state_dict(fixed_state_dict)
model.eval()

# Define transform - same as used in training
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    try:
        # Read the image file and prepare it for prediction
        img = Image.open(file.stream)
        img = transform(img).unsqueeze(0)

        # Make prediction
        with torch.no_grad():
            outputs = model(img)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            prediction_idx = torch.argmax(outputs, dim=1).item()
            confidence = float(probabilities[prediction_idx])

        # Original categories from the model
        categories = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        original_prediction = categories[prediction_idx]
        
        # Map to recyclable/non-recyclable
        is_recyclable = original_prediction != 'trash'
        prediction = 'recyclable' if is_recyclable else 'non_recyclable'

        # If it's recyclable, keep the same confidence
        # If it's non-recyclable (trash), keep the same confidence
        
        # Return response matching the frontend's PredictionResult interface
        return jsonify({
            'prediction': prediction,
            'confidence': confidence  # This will be a float between 0 and 1
        })
    except Exception as e:
        return jsonify({'error': f'Error processing the image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
