import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import tensorflow as tf
import numpy as np
import base64
import io
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this!

class_names = ["Pizza", "Steak"]

# MongoDB connection
try:
    client = MongoClient("mongodb+srv://aryan:aryan@nutrifood.xw6mdsn.mongodb.net/")
    db = client['user_db']
    users_collection = db['users']
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# Nutritionix API credentials
NUTRITIONIX_APP_ID = 'a2e74d94'
NUTRITIONIX_API_KEY = '06ce70516d0251b185d31f4ef0540927'
NUTRITIONIX_API_URL = 'https://trackapi.nutritionix.com/v2/natural/nutrients'


# Add after your existing MongoDB connection
try:
    tracker_collection = db['tracker_entries']
    print("✅ Tracker collection connected successfully!")
except Exception as e:
    print(f"❌ Tracker collection error: {e}")

# Add these new routes after your existing routes

@app.route('/add_to_tracker', methods=['POST'])
def add_to_tracker():
    if 'user' not in session:
        return redirect(url_for('signin'))
    
    try:
        food_item = request.form['food_item']
        quantity = request.form['quantity']
        calories = request.form['calories']
        img_data = request.form.get('img_data', '')
        
        # Extract nutrients from form data
        nutrients = {}
        for key, value in request.form.items():
            if key.startswith('nutrient_'):
                nutrient_name = key.replace('nutrient_', '')
                nutrients[nutrient_name] = value
        
        # Create tracker entry
        tracker_entry = {
            'username': session['user'],
            'food_item': food_item,
            'quantity': quantity,
            'calories': calories,
            'nutrients': nutrients,
            'date': request.form.get('date', ''),
            'meal_type': request.form.get('meal_type', 'lunch'),
            'img_data': img_data,
            'timestamp': request.form.get('timestamp', '')
        }
        
        tracker_collection.insert_one(tracker_entry)
        print(f"✅ Added {food_item} to tracker for {session['user']}")
        
        return redirect(url_for('tracker'))
        
    except Exception as e:
        print(f"❌ Error adding to tracker: {e}")
        return redirect(url_for('home'))

@app.route('/tracker')
def tracker():
    if 'user' not in session:
        return redirect(url_for('signin'))
    
    # Get today's entries
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    
    today_entries = list(tracker_collection.find({
        'username': session['user'],
        'date': today
    }))
    
    # Get monthly data (last 30 days)
    monthly_entries = list(tracker_collection.find({
        'username': session['user'],
        'date': {'$gte': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}
    }))
    
    # Calculate totals
    today_totals = calculate_totals(today_entries)
    monthly_totals = calculate_totals(monthly_entries)
    
    # Get recent entries for display
    recent_entries = list(tracker_collection.find(
        {'username': session['user']}
    ).sort('timestamp', -1).limit(10))
    
    return render_template('tracker.html', 
                         username=session['user'],
                         today_entries=today_entries,
                         monthly_entries=monthly_entries,
                         today_totals=today_totals,
                         monthly_totals=monthly_totals,
                         recent_entries=recent_entries)

@app.route('/delete_entry/<entry_id>')
def delete_entry(entry_id):
    if 'user' not in session:
        return redirect(url_for('signin'))
    
    from bson.objectid import ObjectId
    tracker_collection.delete_one({'_id': ObjectId(entry_id), 'username': session['user']})
    return redirect(url_for('tracker'))

def calculate_totals(entries):
    totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0,
        'sodium': 0,
        'calcium': 0,
        'iron': 0,
        'vitamin_c': 0,
        'vitamin_a': 0
    }
    
    for entry in entries:
        totals['calories'] += float(entry.get('calories', 0))
        
        nutrients = entry.get('nutrients', {})
        for nutrient, value in nutrients.items():
            nutrient_lower = nutrient.lower()
            value_clean = float(''.join(c for c in str(value) if c.isdigit() or c == '.'))
            
            if 'protein' in nutrient_lower:
                totals['protein'] += value_clean
            elif 'carb' in nutrient_lower:
                totals['carbs'] += value_clean
            elif 'fat' in nutrient_lower and 'saturated' not in nutrient_lower:
                totals['fat'] += value_clean
            elif 'fiber' in nutrient_lower:
                totals['fiber'] += value_clean
            elif 'sugar' in nutrient_lower:
                totals['sugar'] += value_clean
            elif 'sodium' in nutrient_lower:
                totals['sodium'] += value_clean
            elif 'calcium' in nutrient_lower:
                totals['calcium'] += value_clean
            elif 'iron' in nutrient_lower:
                totals['iron'] += value_clean
            elif 'vitamin c' in nutrient_lower:
                totals['vitamin_c'] += value_clean
            elif 'vitamin a' in nutrient_lower:
                totals['vitamin_a'] += value_clean
    
    return totals


def custom_binary_crossentropy(*args, **kwargs):
    return tf.keras.losses.BinaryCrossentropy()

try:
    model = tf.keras.models.load_model('food_CNN.h5', custom_objects={'BinaryCrossentropy': custom_binary_crossentropy})
    print("✅ ML Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            error_message = "Invalid credentials. Try again."
    
    return render_template('signin.html', error_message=error_message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        if users_collection.find_one({'username': username}):
            error_message = "Username already exists. Try signing in."
            return render_template('signup.html', error_message=error_message)
        
        users_collection.insert_one({'username': username, 'password': hashed_password})
        session['user'] = username
        return redirect(url_for('home'))
    
    return render_template('signup.html', error_message=error_message)

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('home.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('signin'))

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'GET':
        # Handle GET request from camera redirect
        prediction = request.args.get('prediction')
        img_data = request.args.get('img_data')  # Get image data if available
        if prediction:
            # Don't get nutrition info yet - let user enter quantity first
            return render_template('result.html', 
                                 prediction=prediction, 
                                 img_data=img_data,
                                 nutrition_info=None,  # No nutrition info yet
                                 username=session.get('user'))
        return redirect(url_for('home'))
    
    # POST method for file upload
    if 'user' not in session:
        return redirect(url_for('signin'))
        
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    try:
        img = Image.open(file.stream)

        # Convert image to base64 for display
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        # Make prediction
        if model:
            prediction = predict_image(model, img, class_names)
            print(f"🔍 Predicted: {prediction}")
        else:
            prediction = "Model not available"

        # Don't get nutrition info yet - let user enter quantity first
        return render_template('result.html', 
                             prediction=prediction, 
                             img_data=img_base64, 
                             nutrition_info=None,
                             username=session['user'])
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return render_template('result.html', 
                             prediction=f"Error: {str(e)}", 
                             img_data=None, 
                             nutrition_info=None,
                             username=session['user'])
    
@app.route('/classify-camera', methods=['POST'])
def classify_camera():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'prediction': None, 'error': 'No image data received'}), 400
    
    try:
        image_data = data['image']
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))

        if model:
            prediction = predict_image(model=model, img=image, class_names=class_names)
            # Don't get nutrition info here - let user enter quantity first
        else:
            prediction = "Model not available"
            
        return jsonify({
            'prediction': prediction
            # Remove nutrition_info from here
        })
    except Exception as e:
        return jsonify({'prediction': None, 'error': str(e)}), 500

@app.route('/fetch_nutrition_with_quantity', methods=['POST'])
def fetch_nutrition_with_quantity():
    if 'user' not in session:
        return redirect(url_for('signin'))
        
    food_item = request.form['food_item']
    quantity = request.form['quantity']
    img_data = request.form.get('img_data', '')

    print(f"🔍 Fetching nutrition for {quantity}g of {food_item}")

    # Fetch nutrition information based on the prediction result and the quantity
    nutrition_info = get_nutrition_info(food_item, quantity)

    return render_template('result.html', 
                         prediction=food_item, 
                         nutrition_info=nutrition_info, 
                         img_data=img_data,
                         username=session['user'])

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def predict_image(model, img, class_names):
    if img.mode == 'RGBA':
        img = img.convert('RGB')  

    img = tf.image.resize(np.array(img), size=[224, 224])  
    img = img / 255.0
    prediction = model.predict(tf.expand_dims(img, axis=0)) 
    predicted_class = class_names[int(tf.round(prediction))]
    return predicted_class

def get_nutrition_info(food_item, quantity=None):
    if quantity is None or quantity == '':
        quantity = 100
    
    headers = {
        'x-app-id': NUTRITIONIX_APP_ID,
        'x-app-key': NUTRITIONIX_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Format the query
    query = f"{quantity}g {food_item}"
    
    data = {
        "query": query,
        "timezone": "US/Eastern"
    }
    
    print(f"🔍 Making Nutritionix API call: {query}")
    
    try:
        response = requests.post(NUTRITIONIX_API_URL, json=data, headers=headers, timeout=10)
        print(f"🔍 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            nutrition_data = response.json()
            foods = nutrition_data.get('foods', [])
            
            if foods:
                food = foods[0]  # Take the first result
                
                # Extract nutrition information using the exact field names from the API
                calories = food.get('nf_calories', 0)
                serving_weight = food.get('serving_weight_grams', quantity)
                
                # Get ALL nutrients with proper formatting
                nutrients = {
                    'Protein': f"{food.get('nf_protein', 0):.1f} g",
                    'Total Fat': f"{food.get('nf_total_fat', 0):.1f} g",
                    'Saturated Fat': f"{food.get('nf_saturated_fat', 0):.1f} g",
                    'Carbohydrates': f"{food.get('nf_total_carbohydrate', 0):.1f} g",
                    'Sugars': f"{food.get('nf_sugars', 0):.1f} g",
                    'Fiber': f"{food.get('nf_dietary_fiber', 0):.1f} g",
                    'Cholesterol': f"{food.get('nf_cholesterol', 0):.1f} mg",
                    'Sodium': f"{food.get('nf_sodium', 0):.1f} mg",
                    'Potassium': f"{food.get('nf_potassium', 0):.1f} mg"
                }
                
                print(f"✅ Successfully got nutrition data from Nutritionix")
                
                return {
                    'calories': calories,
                    'total_weight': f"{serving_weight}g",
                    'diet_labels': [],
                    'health_labels': [],
                    'meal_type': 'N/A',
                    'dish_type': 'N/A',
                    'cuisine_type': 'N/A',
                    'nutrients': nutrients
                }
            else:
                print("❌ No food data found in Nutritionix response")
                return get_fallback_nutrition(food_item, quantity)
        else:
            print(f"❌ Nutritionix API Error: {response.status_code} - {response.text}")
            return get_fallback_nutrition(food_item, quantity)
            
    except Exception as e:
        print(f"❌ Nutritionix API error: {e}")
        return get_fallback_nutrition(food_item, quantity)

def get_fallback_nutrition(food_item, quantity):
    """Fallback nutrition data"""
    if quantity is None or quantity == '':
        quantity = 100
    
    try:
        quantity_num = float(quantity)
    except:
        quantity_num = 100
    
    scale = quantity_num / 100.0
    
    if food_item == "Steak":
        return {
            'calories': int(271 * scale),
            'total_weight': f'{quantity}g',
            'diet_labels': ['HIGH_PROTEIN', 'LOW_CARB'],
            'health_labels': ['SUGAR_CONSCIOUS', 'KETO_FRIENDLY'],
            'meal_type': 'lunch/dinner',
            'dish_type': 'main course',
            'cuisine_type': 'american',
            'nutrients': {
                'Protein': f'{25 * scale:.1f} g',
                'Total Fat': f'{19 * scale:.1f} g',
                'Saturated Fat': f'{8 * scale:.1f} g',
                'Carbohydrates': f'{0 * scale:.1f} g',
                'Sugars': f'{0 * scale:.1f} g',
                'Fiber': f'{0 * scale:.1f} g',
                'Cholesterol': f'{85 * scale:.1f} mg',
                'Sodium': f'{65 * scale:.1f} mg',
                'Potassium': f'{350 * scale:.1f} mg'
            }
        }
    elif food_item == "Pizza":
        return {
            'calories': int(285 * scale),
            'total_weight': f'{quantity}g',
            'diet_labels': ['BALANCED'],
            'health_labels': ['VEGETARIAN'],
            'meal_type': 'lunch/dinner',
            'dish_type': 'main course', 
            'cuisine_type': 'italian',
            'nutrients': {
                'Protein': f'{12 * scale:.1f} g',
                'Total Fat': f'{10 * scale:.1f} g',
                'Saturated Fat': f'{4 * scale:.1f} g',
                'Carbohydrates': f'{36 * scale:.1f} g',
                'Sugars': f'{3 * scale:.1f} g',
                'Fiber': f'{2 * scale:.1f} g',
                'Cholesterol': f'{18 * scale:.1f} mg',
                'Sodium': f'{640 * scale:.1f} mg',
                'Potassium': f'{180 * scale:.1f} mg'
            }
        }
    else:
        return {
            'calories': 'N/A',
            'total_weight': f'{quantity}g',
            'diet_labels': [],
            'health_labels': [],
            'meal_type': 'N/A',
            'dish_type': 'N/A',
            'cuisine_type': 'N/A',
            'nutrients': {}
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # This is for Vercel serverless
    application = app