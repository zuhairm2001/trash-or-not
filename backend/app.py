from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import os
from torchvision import transforms, models
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load the model
device = torch.device("cpu")
model = models.resnet34(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 2)  # Binary classification (recyclable/non-recyclable)
model.load_state_dict(torch.load('model.pth', map_location=device))
model.eval()

# Define transform
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
            _, predicted = torch.max(outputs, 1)

        # Map the prediction to a label
        recyclable = ['recyclable', 'non_recyclable']
        category = recyclable[predicted.item()]

        return jsonify({
            'prediction': category,
            'confidence': float(torch.nn.functional.softmax(outputs, dim=1)[0][predicted.item()])
        })
    except Exception as e:
        return jsonify({'error': f'Error processing the image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
