from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Secret key for session management

# Ensure the 'uploads' folder exists
os.makedirs('uploads', exist_ok=True)

# Function to initialize the database
def initialize_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

# Load the trained model
model = load_model(r'D:\flask\forest_fire_model.h5')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()

        if row:
            # Check if the provided password matches the stored hashed password
            if check_password_hash(row[0], password):
                session['logged_in'] = True
                print("Login successful. Redirecting to index page...")
                return redirect(url_for('index'))  # Redirect to index page after successful login
        
        # If username doesn't exist or password is incorrect, show error
        error = 'Invalid username or password'
        print("Login failed. Error:", error)
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session and session['logged_in']:
        print("User logged in. Rendering index page...")
        return render_template('index.html')  # Render index page if logged in
    else:
        print("User not logged in. Redirecting to login page...")
        return redirect(url_for('login'))  # Redirect to login page if not logged in

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    # Image preprocessing and prediction logic
    img = image.load_img(file_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)
    result = np.round(prediction).astype(int)[0][0]

    # Define the response based on the prediction
    prediction_text = 'No Fire' if result == 1 else 'Fire'

    return jsonify({'prediction': prediction_text})

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/services', methods=['GET'])
def services():
    return render_template('services.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database and insert user data
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
            print("Signup successful. Redirecting to login page...")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = 'Username already exists. Please choose a different one.'
            return render_template('signup.html', error=error)
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
