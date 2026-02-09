# Smart Dent AI

Smart Dent AI is an intelligent oral health monitoring application designed to provide accessible dental care guidance. It is particularly aimed at assisting children, the elderly, and residents of rural areas. The application allows users to monitor their oral health daily, helping to prevent dental issues before they become painful or costly.

## Features

- **AI-Powered Dental Analysis**: Utilizes computer vision to analyze images of teeth.
- **Early Issue Detection**: Identifies early signs of plaque buildup, gum inflammation, and other common dental problems.
- **Daily Guidance**: Provides personalized brushing tips and oral care recommendations.
- **User-Friendly Interface**: Simple and intuitive interface for capturing images and viewing results.
- **Health Dashboard**: Displays an overall health score and tracks progress over time.
- **Accessible**: Designed for communities with limited access to dental professionals.

## How It Works

The project consists of three main components:

1.  **Frontend**: A web interface built with HTML, CSS, and vanilla JavaScript. It allows users to capture an image of their teeth using their device's camera.
2.  **Backend**: A Python server built with Flask. It receives the image from the frontend, processes it, and returns the analysis results.
3.  **AI Model**: The backend uses a computer vision model to analyze the submitted image. The current implementation in `backend/model.py` uses OpenCV to perform rule-based analysis for things like tooth yellowness and other visible irregularities.

Additionally, the `oral_conditon_chek.py` file contains a deep learning model built with TensorFlow/Keras for tooth detection (bounding box prediction). This model is not currently integrated into the Flask backend but represents a potential future direction for the AI analysis.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7+
- `pip` (Python package installer)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd smart_dent_ai
    ```

2.  **Install backend dependencies:**
    The backend relies on several Python packages. You can install them using `pip`:
    ```bash
    pip install flask flask-cors numpy pillow opencv-python
    ```
    *Note: It is highly recommended to use a virtual environment to manage your Python dependencies.*

3.  **Run the backend server:**
    ```bash
    python backend/app.py
    ```
    The server will start on `http://localhost:5000`.

### Usage

1.  Open your web browser and navigate to `http://localhost:5000`.
2.  Click on the "Start AI Scan" button to activate your camera.
3.  Position your mouth within the frame and click "Capture Image".
4.  Click the "Analyze" button to send the image to the backend for analysis.
5.  The results of the analysis will be displayed on the page.

## Project Structure

```
.
├── backend/
│   ├── app.py          # Flask backend server
│   └── model.py        # AI model for dental analysis (OpenCV-based)
├── frontend/
│   ├── app.js          # Frontend JavaScript for camera interaction and UI
│   ├── index.html      # Main HTML file for the application
│   └── style.css       # Styles for the frontend
├── oral_conditon_chek.py # Jupyter notebook for training the TensorFlow model
├── README.md           # This file
└── ...
```

## Future Improvements

- **Integrate the TensorFlow Model**: Replace the current OpenCV-based analysis in `model.py` with the more advanced TensorFlow model from `oral_conditon_chek.py` for more accurate tooth detection.
- **Enhanced Design**: Improve the UI/UX with more modern styling and animations.
- **Advanced Dashboard**: Add features to the dashboard to track oral health trends over time.
- **User Accounts**: Implement user authentication to save and view historical scan data.
