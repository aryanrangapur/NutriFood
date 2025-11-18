# NutriFood - Food Classification & Nutrition Tracker

## Project Description

NutriFood is a web application that uses machine learning to classify food images and provide detailed nutritional information. Users can upload food images or use their camera to identify foods and track their daily nutrition intake.

## Features

- **Food Image Classification**: Upload images or use camera to identify food items (Pizza, Steak)
- **Nutrition Analysis**: Get detailed nutritional information for identified foods
- **User Authentication**: Secure signup and login system
- **Nutrition Tracker**: Track daily calorie and nutrient intake
- **Camera Integration**: Real-time food classification using device camera
- **Responsive Design**: Works on both desktop and mobile devices

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MongoDB
- **Machine Learning**: TensorFlow with custom CNN model
- **APIs**: Nutritionix API for nutrition data
- **Authentication**: Session-based with password hashing

### Frontend
- **HTML5** with responsive CSS
- **JavaScript** for dynamic interactions
- **Camera API** for real-time image capture

### Deployment
- **Platform**: Railway
- **Port**: 8080
- **URL**: [https://nutrifood.onrender.com/](https://nutrifood.onrender.com/)

## Project Structure

```
nutrifood/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── food_CNN.h5           # Trained ML model
├── static/
│   └── style.css         # Main stylesheet
└── templates/
    ├── home.html         # Main dashboard
    ├── signin.html       # Login page
    ├── signup.html       # Registration page
    ├── result.html       # Classification results
    └── tracker.html      # Nutrition tracker
```

## Installation & Local Development

### Prerequisites
- Python 3.11+
- MongoDB database
- Nutritionix API account

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nutrifood
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```
   SECRET_KEY=your-secret-key
   MONGODB_URI=your-mongodb-connection-string
   NUTRITIONIX_APP_ID=your-nutritionix-app-id
   NUTRITIONIX_API_KEY=your-nutritionix-api-key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open http://localhost:5000 in your browser

## API Endpoints

### Authentication
- `POST /signin` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### Food Classification
- `POST /classify` - Classify uploaded food image
- `POST /classify-camera` - Classify image from camera
- `POST /fetch_nutrition_with_quantity` - Get nutrition data

### Nutrition Tracking
- `POST /add_to_tracker` - Add food to nutrition tracker
- `GET /tracker` - View tracker data
- `DELETE /delete_entry/<entry_id>` - Remove tracker entry

## Machine Learning Model

- **Model Type**: Convolutional Neural Network (CNN)
- **Classes**: Pizza, Steak
- **Framework**: TensorFlow
- **Input Size**: 224x224 pixels

## Database Schema

### Users Collection
```javascript
{
  username: String,
  password: String (hashed)
}
```

### Tracker Entries Collection
```javascript
{
  username: String,
  food_item: String,
  quantity: String,
  calories: Number,
  nutrients: Object,
  meal_type: String,
  date: String,
  timestamp: String
}
```

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask session secret
- `MONGODB_URI`: MongoDB connection string
- `NUTRITIONIX_APP_ID`: Nutritionix application ID
- `NUTRITIONIX_API_KEY`: Nutritionix API key

### Dependencies
Key Python packages:
- Flask 2.3.3
- TensorFlow 2.16.2
- PyMongo 4.6.3
- Pillow 10.3.0
- Requests 2.31.0

## Deployment

The application is deployed on Railway with the following configuration:

- **Runtime**: Python 3.11.9
- **Build Command**: Automatic dependency installation
- **Start Command**: `python app.py`
- **Port**: 8080 (auto-configured by Railway)

## Usage

1. **Registration/Login**: Create an account or sign in
2. **Food Classification**: 
   - Upload food images or use camera
   - View classification results
3. **Nutrition Information**:
   - Enter food quantity
   - View detailed nutrition facts
4. **Tracking**:
   - Add foods to daily tracker
   - Monitor calorie and nutrient intake
   - View history and trends

## Future Enhancements

- Expand food classification to more categories
- Add meal planning features
- Implement progress charts and analytics
- Add social features and sharing
- Support for multiple languages


## Live Demo

Access the live application at: [https://nutrifood.onrender.com/](https://nutrifood.onrender.com/)
