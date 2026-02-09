from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import base64
import json
from datetime import datetime
import numpy as np
from PIL import Image
import io
import cv2
import time
import logging

# Import the enhanced model
from model import DentalAIModel

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI model
dental_ai = DentalAIModel()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_base64_image(image_data):
    """Decode base64 image data to PIL Image"""
    try:
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return None

def validate_image_quality(image):
    """Validate image quality for dental analysis"""
    try:
        # Check image size
        width, height = image.size
        if width < 200 or height < 200:
            return False, "Image too small. Please use a higher resolution image."
        
        # Check if image is too dark
        image_array = np.array(image)
        mean_brightness = np.mean(image_array)
        if mean_brightness < 50:
            return False, "Image too dark. Please take photo with better lighting."
        
        # Check if image is too bright (overexposed)
        if mean_brightness > 240:
            return False, "Image too bright. Please reduce lighting or avoid flash."
        
        return True, "Image quality acceptable"
    except Exception as e:
        logger.error(f"Error validating image: {e}")
        return False, "Error validating image quality"

def convert_numpy_to_python_types(obj):
    """
    Recursively converts numpy types (integers, floats, booleans, ndarray) to standard Python types.
    """
    if isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8,
                       np.int16, np.int32, np.int64, np.uint8,
                       np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python_types(elem) for elem in obj]
    return obj

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    return send_from_directory('../frontend', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': dental_ai.is_model_loaded(),
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_dental_image():
    """Main endpoint for dental image analysis"""
    try:
        start_time = time.time()
        
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        
        # Check for image data
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image = decode_base64_image(data['image'])
        if image is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Validate image quality
        is_valid, message = validate_image_quality(image)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Save uploaded image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dental_image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath, 'JPEG', quality=95)
        
        # Perform AI analysis
        try:
            analysis_result = dental_ai.analyze_dental_image(image)
            analysis_result_clean = convert_numpy_to_python_types(analysis_result)
            
            # Add processing time
            processing_time = round(time.time() - start_time, 2)
            analysis_result_clean['processing_time'] = processing_time
            analysis_result_clean['image_path'] = filepath
            
            logger.info(f"Analysis completed in {processing_time}s")
            
            return jsonify({
                'success': True,
                'result': analysis_result_clean,
                'message': 'Analysis completed successfully'
            })
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return jsonify({'error': 'Analysis failed. Please try again.'}), 500
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint for direct file uploads"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Convert to PIL Image and validate
        image = Image.open(filepath)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        is_valid, message = validate_image_quality(image)
        if not is_valid:
            os.remove(filepath)  # Clean up invalid file
            return jsonify({'error': message}), 400
        
        # Convert to base64 for response
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image_data': f"data:image/jpeg;base64,{image_base64}",
            'filename': filename,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({'error': 'File upload failed'}), 500

@app.route('/api/history', methods=['GET'])
def get_analysis_history():
    """Get analysis history (mock endpoint)"""
    try:
        # In a real application, this would fetch from a database
        history = []
        upload_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        for filename in sorted(upload_files, reverse=True)[:10]:  # Last 10 files
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            stat = os.stat(filepath)
            
            history.append({
                'filename': filename,
                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size,
                'status': 'completed'
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """Get model information"""
    try:
        model_info = dental_ai.get_model_info()
        return jsonify({
            'success': True,
            'model_info': model_info
        })
    except Exception as e:
        logger.error(f"Model info error: {e}")
        return jsonify({'error': 'Failed to get model information'}), 500

@app.route('/api/model/reload', methods=['POST'])
def reload_model():
    """Reload the AI model"""
    try:
        dental_ai.reload_model()
        return jsonify({
            'success': True,
            'message': 'Model reloaded successfully'
        })
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        return jsonify({'error': 'Failed to reload model'}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        
        if not data or 'feedback' not in data:
            return jsonify({'error': 'No feedback provided'}), 400
        
        # In a real application, save feedback to database
        feedback_data = {
            'feedback': data['feedback'],
            'rating': data.get('rating'),
            'timestamp': datetime.now().isoformat(),
            'user_id': data.get('user_id', 'anonymous')
        }
        
        # Log feedback for now
        logger.info(f"Feedback received: {feedback_data}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('frontend', exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Start the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=os.environ.get('DEBUG', 'False').lower() == 'true'
    )